import pandas as pd
import psycopg2
from data_model import *
import sys, os
from algs import min_intra_min_inter, max_intra_max_inter, max_intra_min_inter, min_intra_max_inter
from scipy.spatial import distance
import click
import codecs


with open('genres.txt') as f :
    #Makes a dictionary of features where the key is in the format of Answer.keyword
    features = {'Answer.genre{:02}'.format(i+1):k.strip() for i,k in enumerate(f.readlines())}
    #print(features)

def print_songs(f, dir_path, w, songs, k, l, alg):
    playlist_id = {"min_intra_max_inter": 1, "min_intra_min_inter": 2, "max_intra_min_inter": 3, "max_intra_max_inter": 4, "no_diversity": 5}
    indent = "      "
    set_count = 1

    f.write('    {\n' + indent + '"playlist_id" : ' + str(playlist_id[alg]) + ",\n" + indent + '"sets":[\n')

    for i in range(k):
        f.write(indent + '  {\n')
        indent = indent + '    '
        f.write(indent + '"set_id" : ' + str(set_count) + ',\n')
        f.write(indent + '"songs" : [\n')

        j_count = 1
        for j in songs[i]:

            s = Song.get(Song.song_id==j)
            f.write(indent + '  {\n')
            indent = indent + '    '
            f.write(indent + '"song_id" : ' + str(j) + ",\n")
            f.write(indent + '"song_title" : "' + s.title.replace('"','\\\"') + '",\n')
            f.write(indent + '"artist" : "' + s.artist.replace('"','\\\"') + '",\n')
            f.write(indent + '"album" : "' + s.album.replace('"','\\\"') + '",\n')
            f.write(indent + '"duration" : "' + s.duration + '"\n')
            indent = '          '
            if (j_count < len(songs[i])):
                f.write(indent + '  },\n')
            else:
                f.write(indent + '  }\n')
                f.write(indent + ']\n')

            j_count = j_count + 1

        indent = '      '

        if (set_count < k):
             f.write(indent + '  },\n')
        else:
            f.write(indent + '  }\n')
            f.write(indent + ']\n')

        set_count = set_count + 1

    if int(playlist_id[alg]) < 5:
        f.write('    },\n')
    else:
        f.write('    }\n')
        f.write('  ]\n')

def getSimilarSongs(w, worker_profile, k, l):
    banned_artists = worker_profile.loc[w, 'BannedArtists'].strip('][').replace("'", "").split(', ') 
    ok_genres = worker_profile.loc[w, 'OKGenres'].strip('][').replace("'", "").split(', ') 

    where_stmt="("
    for g in ok_genres:
        where_stmt = where_stmt + "(genre LIKE '%" + g + "%') OR "
    where_stmt = where_stmt[:len(where_stmt)-4] + ") AND NOT ("

    for a in banned_artists:
        where_stmt = where_stmt + " artist = '" + a + "' OR "
    where_stmt = where_stmt[:len(where_stmt)-4] + ") AND period = 2000"

    select_stmt = "SELECT song_id, title, artist, tempo, period, duration, popularity, genre FROM song "
    select_stmt = select_stmt + "WHERE " + where_stmt + "ORDER BY random() LIMIT " + str(k*l)

    conn = psycopg2.connect(database = "postgres", user = "user")
    cur = conn.cursor()
    cur.execute(select_stmt)
    worker_songs = cur.fetchall()

    if (len(worker_songs) < (k*l)):
        select_stmt = "SELECT song_id, title, artist, tempo, period, duration, popularity, genre FROM song WHERE period = 2000 ORDER BY random() LIMIT " + str(k*l)
        cur.execute(select_stmt)
        worker_songs = cur.fetchall()
        print("Too many restrictions");
    conn.close()

    grouping = []
    song_list = []

    for s in worker_songs:
        song_list.append(s[0])

    a = 0
    b = 9

    for i in range(5):
        grouping.append(song_list[a:b])
        a = a + 10
        b = b + 10

    return grouping

# def getSimilarSongs(num_sessions, session_length):
#     grouping = []

#     period = 2000 #randomly selected
#     songs = Song.select().where(Song.period == period).order_by(fn.Random()).limit(num_sessions * session_length)
#     song_list = []

#     for s in songs:
#         song_list.append(s.song_id)

#     a = 0
#     b = 9

#     for i in range(5):
#         grouping.append(song_list[a:b])
#         a = a + 10
#         b = b + 10

#     return grouping


def select_good_songs(w, worker_profile, k, l, dim1, dim2):
    banned_artists = worker_profile.loc[w, 'BannedArtists'].strip('][').replace("'", "").split(', ') 
    ok_genres = worker_profile.loc[w, 'OKGenres'].strip('][').replace("'", "").split(', ') 

    where_stmt="("
    for g in ok_genres:
        where_stmt = where_stmt + "(genre LIKE '%" + g + "%') OR "
    where_stmt = where_stmt[:len(where_stmt)-4] + ") AND NOT ("

    for a in banned_artists:
        where_stmt = where_stmt + " artist = '" + a + "' OR "
    where_stmt = where_stmt[:len(where_stmt)-4] + ")"

    select_stmt = "SELECT song_id, title, artist, tempo, period, duration, popularity, genre FROM song "
    select_stmt = select_stmt + "WHERE " + where_stmt + " ORDER BY random() LIMIT " + str(k*l)

    conn = psycopg2.connect(database = "postgres", user = "user")
    cur = conn.cursor()

    cur.execute(select_stmt)
    worker_songs = cur.fetchall()

    conn.close()

    SONG_ID = 0
    TEMPO = 3
    PERIOD = 4
    POPULARITY = 6
    GENRE = 7
    DIM1 = -1
    DIM2 = -1

    if (dim1 == 'tempo'):
        DIM1 = TEMPO
    elif (dim1 == 'period'):
        DIM1 = PERIOD
    elif (dim1 == 'popularity'):
        DIM1 = POPULARITY

    if (dim2 == 'tempo'):
        DIM2 = TEMPO
    elif (dim2 == 'period'):
        DIM2 = PERIOD
    elif (dim2 == 'popularity'):
        DIM2 = POPULARITY

    if 'genre' in dim1:
        #get random songs where worker genres
        songs = {str(t[SONG_ID]): (sum(worker_profile.loc[w,t[GENRE].split(", ")].values), t[DIM2]) for t in worker_songs}

    elif 'genre' in dim2:
        songs = {str(t[SONG_ID]): (t[DIM1], sum(worker_profile.loc[w,t[GENRE].split(", ")].values)) for t in worker_songs}
    else:
        songs = {str(t[SONG_ID]): (t[DIM1], t[DIM2]) for
                 t in worker_songs}

    print (w, dim1, dim2, "Songs:", songs)
    return songs

def getContext(dim1, dim2):
    #Suppose you are thinking of a playlist to listen to CONTEXT, we generated 5 playlists for you, each with 3 sets.

    context = "none"

    if dim1 == "tempo" and dim2 == "popularity":
        context = "during a long drive"
    elif dim1 == "period" and dim2 == "genre":
        context = "in a theme party"
    elif dim1 == "popularity" and dim2 == "genre":
        context = "when learning about a music style"
    elif dim1 == "genre" and dim2 == "tempo":
        context = "on a Sunday morning"

    return context

#process command line arguments
@click.command()
@click.argument('worker_profiles_path', type=click.Path(exists=True))
@click.argument('num_sessions', default=5, type=click.INT)
@click.argument('session_length', default=10, type=click.INT)
@click.option('--dim1', help="Which dimension of song to use",
              type=click.Choice(['tempo','genre', 'popularity', 'period']), default="popularity")
@click.option('--dim2', help="Which dimension of song to use",
              type=click.Choice(['tempo','genre', 'popularity', 'period']), default="tempo")
#main program
def main(worker_profiles_path, num_sessions, session_length, dim1='popularity', dim2='tempo'):

    workers = pd.read_csv(worker_profiles_path, encoding='latin')
    print("READ %s number of workers ..." % workers.shape[0])
    cols = ['WorkerId', 'Answer.BannedArtists[]']
    cols.extend(list(features.keys()))

    worker_columns = list(features.values())
    worker_columns.append("OKGenres")
    worker_columns.append("BannedArtists")

    worker_genres = pd.DataFrame(0, columns=worker_columns, index=workers.WorkerId)

    #worker_genres  contains the ratings to the genres given by the workers

    for i, wk in workers.loc[:,cols].iterrows():
        ok_genres=[]
        banned_artists = wk[1].encode("utf-8").split("|")

        for feat in features:
            if (getattr(wk,feat) > 0 ):
                worker_genres.loc[wk.WorkerId, features[feat]] = getattr(wk,feat)
                if worker_genres.loc[wk.WorkerId, features[feat]] > 1:
                    ok_genres.append(features[feat])

        worker_genres.loc[wk.WorkerId, "OKGenres"] = str(ok_genres).encode("utf-8")
        worker_genres.loc[wk.WorkerId, "BannedArtists"] = str(banned_artists).encode("utf-8")

    print("Generating playlists...")

    for w in sorted(worker_genres.index):
        filename = "data/playlists/" + w + ".json"
        context = getContext(dim1, dim2)

        f = codecs.open(filename, 'w', encoding='utf8') 
        f.write('{\n  "worker_id"  : "' + w + '",\n  "context" : "' + context + '",\n  "playlists" : [\n')
        
        songs = select_good_songs(w, worker_genres, num_sessions, session_length, dim1, dim2)
        grouping = min_intra_max_inter(songs, num_sessions, session_length)
        print_songs(f, 'ours', w, grouping, num_sessions, session_length, "min_intra_max_inter")

        songs = select_good_songs(w, worker_genres, num_sessions, session_length, dim1, dim2)
        grouping = min_intra_min_inter(songs, num_sessions, session_length)
        print_songs(f, 'ours', w, grouping, num_sessions, session_length, "min_intra_min_inter")

        songs = select_good_songs(w, worker_genres, num_sessions, session_length, dim1, dim2)
        grouping = max_intra_min_inter(songs, num_sessions, session_length)
        print_songs(f, 'ours', w, grouping, num_sessions, session_length, "max_intra_min_inter")

        songs = select_good_songs(w, worker_genres, num_sessions, session_length, dim1, dim2)
        grouping = max_intra_max_inter(songs, num_sessions, session_length)
        print_songs(f, 'ours', w, grouping, num_sessions, session_length, "max_intra_max_inter")

        grouping = getSimilarSongs(w, worker_genres, num_sessions, session_length)
        print_songs(f, 'ours', w, grouping, num_sessions, session_length, "no_diversity")

        f.write('}\n')
        f.close()

if __name__ == '__main__':
    main()

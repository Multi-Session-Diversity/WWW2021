# Multi-Session Diversity to Improve User Satisfaction in Web Applications

Real Data Experiments:

-Music Recomendation

+--music-exps-survey: web app where users evaluated playlists recommendations

+--music-generator: source code for generating playlist recommendations

+--results: results of the evaluations

-Task Recomendation

+--results

+--Long-Sessions: raw data in .db of the long sessions. Analysis is in long-sessions-summary.
			
+--Short-Sessions: raw data in .db of the short sessions. Analysis is in short-sessions-summary.

+--music-generator: source code for generating task recommendations

+--task-generator: web app for workers to complete generated tasks

Dataset Description:

These are the new datasets created from various sources. They are Python Pickled files that are in the format of dict

song_id : (first-dimension, second-dimension)

example:

data = {

...

992: (289.2273, 0.499617040318),

993: (235.88526, 0.431673556862),

994: (253.67465, 0.460225344488),

995: (314.17424, 0.14468466091),

996: (366.70649, 0.417017294763),

997: (578.89914, 0.512226738318),

998: (239.56853, 0.542883760596),

999: (325.53751, 0.424360539044),

...

}

Datasets :

d1_duration_hotness.p : Dataset produced from 1-M-Songs Dataset Meta Data containing :

	•	first_dim : Song duration

	•	second_dim : artist_hotttnesss

d2_release_artist_familiarity.p: Dataset produced from 1-M-Songs Dataset Meta Data containing :

	•	first_dim : Song release year

	•	second_dim : artist_familiarity

d3_tempo_loudness.p : Dataset produced from songsdata.csv :

	•	first_dim : Song tempo

	•	second_dim : Song loudness


Codes:
	Implementation of the algorithms are inside the "qual_analysis" folder 


Use the following commands to compile the codes:
	
	Before doing so, ensure your current directory is the "Qual_Analysis" folder. Then type as below: 

	▪	Python simulationRunner——MMRAtOnce.py     (To run mmr)

	▪	Python simulationRunner—OurAlgAtOnce.py   (To run our algorithms)

	▪	Python randomalg_simulation.py          (To run the random algorithm)

	Provide inputs as per the click commands. The results will be stored in the res folder upon running algorithms. 
	

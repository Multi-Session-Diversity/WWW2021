<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
    <head>
        <meta charset="utf-8">
	    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <title>Playlist Recommendations</title>
        <link href="{{ asset('css/app.css') }}" rel="stylesheet">
        <link href="{{ asset('css/survey.css') }}" rel="stylesheet">
    </head>
    <body>
    <div class="container mt-5 mb-5">
		<p>Thank you for accepting this task, <strong>{{ $contents['worker_id'] }}.</strong></p>

		<p>Suppose you are thinking of a playlist to listen to <strong>{{ $contents['context'] }}</strong>, we generated {{ $num_playlists}} playlists for you, each with {{ $num_sets }} sets.</p>

		Please go over the playlist <b> carefully </b> and do the following:
		<ol>
			<li>Select which songs that you would actually listen to.</li>
			<li>Rate the playlist.</li>
		</ol>
		<br>

		<ul class="nav nav-tabs">
  			@foreach($contents['playlists'] as $playlist)
  			<li class="nav-item">
	    		@if ($loop->first)
	    		<a class="nav-link active" data-toggle="tab" href="#playlist{{$playlist['playlist_id']}}">
	    		@else
	    		<a class="nav-link" data-toggle="tab" href="#playlist{{$playlist['playlist_id']}}">
	    		@endif
	    		Playlist {{$playlist['playlist_id']}}</a>
			</li>
			@endforeach
		</ul>
	
		<form method="POST" action="/submit">
		<input type="hidden" name="worker-id" value="{{ $contents['worker_id'] }}">
		<input type="hidden" name="context" value="{{ $contents['context'] }}">
	    @csrf

		<div class="tab-content">
			@foreach($contents['playlists'] as $playlist)
				@if ($loop->first)
		  		<div class="tab-pane container active" id="playlist{{$playlist['playlist_id']}}">
		  		@else
		  		<div class="tab-pane container fade" id="playlist{{$playlist['playlist_id']}}">
		  		@endif
			  		<div class="mt-3 mb-3">
			  			<h3 class="text-center">Playlist {{$playlist['playlist_id']}}</h3>
			  			<h5 class="text-center">Duration:  {{ $playlist['duration'] }}</h5>

					@foreach($playlist['sets'] as $set)
			  			<h5>Set {{ $set['set_id'] }}</h5>
			  			<table class="table table-striped mb-5">
						  <thead>
						    <tr>
						      <th scope="col"></th>
						      <th scope="col">Song Title</th>
						      <th scope="col">Album</th>
						      <th scope="col">Artist</th>
						      <th scope="col">Duration</th>
						    </tr>
						  </thead>
						  <tbody>
						  	@foreach($set['songs'] as $song)
						    <tr>
						      <th scope="row">
						      	<div class="form-check">
						      	<input type="hidden" name="playlist-{{ $playlist['playlist_id'] }}-total[]" value="0">
  								<input class="form-check-input position-static" type="checkbox" name="playlist-{{ $playlist['playlist_id'] }}-songs[]"  value="{{ $song['song_id'] }}" aria-label="...">
								</div>
							  </th>
						      <td>{{ $song['song_title']}}</td>
						      <td>{{ $song['album']}}</td>
						      <td>{{ $song['artist']}}</td>
						      <td>{{ $song['duration']}}</td>
						    </tr>
						    @endforeach
						    <tr>
						     <th scope="row" colspan="4" class="text-right"> Set Duration</th>
						     <td> {{ $set['duration'] }} </td>
						    </tr>
						  </tbody>
						</table>
			  		@endforeach

			  		<h5>How much do you like this playlist?</h5>
			  		<div class="w-50 ml-3 mb-2">
			  			<table class="table table-borderless">
			  			<thead>
						    <tr>
						      <th scope="col"></th>
						      <th scope="col">Absolutely No</th>
						      <th scope="col">No</th>
						      <th scope="col">Neutral</th>
						      <th scope="col">Yes</th>
						      <th scope="col">Absolutely Yes</th>
						    </tr>
						  </thead>
						  <tbody>
						    <tr>
						      <th scope="row">Artists<br><small><em>Do you like the artists included?</em></small></th>
						      		@for ($i = 1; $i <= 5; $i++)
						      			<td><input class="position-static" value="{{ $i }}" id="{{ $i }}" name="playlist-{{ $playlist['playlist_id'] }}-artists" type="radio" aria-label="..."></td>
						      		@endfor
						    </tr>
						    <tr>
						      <th scope="row">Diversity<br><small><em>Do you like the diversity of songs?</em></small></th>
						      		@for ($i = 1; $i <= 5; $i++)
						      			<td><input class="position-static" value="{{ $i }}" id="{{ $i }}" name="playlist-{{ $playlist['playlist_id'] }}-diversity" type="radio" aria-label="..."></td>
						      		@endfor
						    </tr>
						    <tr>
						      <th scope="row">Recency<br><small><em>Do you like the recency of the songs?</em></small></th>
						      		@for ($i = 1; $i <= 5; $i++)
						      			<td><input class="position-static" value="{{ $i }}" id="{{ $i }}" name="playlist-{{ $playlist['playlist_id'] }}-recency" type="radio" aria-label="..."></td>
						      		@endfor
						    </tr>
						    <tr>
						      <th scope="row">Familiarity<br><small><em>Are you familiar with the songs?</em></small></th>
						      		@for ($i = 1; $i <= 5; $i++)
						      			<td><input class="position-static" value="{{ $i }}" id="{{ $i }}" name="playlist-{{ $playlist['playlist_id'] }}-familiarity" type="radio" aria-label="..."></td>
						      		@endfor
						    </tr>
						    <tr>
						      <th scope="row">Overall Rating<br><small><em>What is your overall rating for this playlist?</em></small></th>
						      <td><input class="position-static" value="1" id="1" name="playlist-{{ $playlist['playlist_id'] }}-overall" type="radio" aria-label="..."><br>Very Bad</td>
						      <td><input class="position-static" value="2" id="2" name="playlist-{{ $playlist['playlist_id'] }}-overall" type="radio" aria-label="..."><br>Bad</td>
						      <td><input class="position-static" value="3" id="3" name="playlist-{{ $playlist['playlist_id'] }}-overall" type="radio" aria-label="..."><br>Neutral</td>
						      <td><input class="position-static" value="4" id="4" name="playlist-{{ $playlist['playlist_id'] }}-overall" type="radio" aria-label="..."><br>Good</td>
						      <td><input class="position-static" value="5" id="5" name="playlist-{{ $playlist['playlist_id'] }}-overall" type="radio" aria-label="..."><br>Very Good</td>
						    </tr>
						  </tbody>
			  			</table>
			  		</div>

			  		</div>

			  		@if(!$loop->first)
			  		<button type="button" class="btn btn-secondary previous-tab float-left">< Previous</button>
					@endif
					@if(!$loop->last)
					<button type="button" class="btn btn-secondary next-tab float-right">Next ></button>
		  			@else
		  			<input type="hidden" name="playlist-count" value="{{ $loop->iteration }}">
		  			<button type="submit" class="btn btn-primary submit float-right">Submit</button>
		  			@endif
		  		</div>
		  	@endforeach
		</div>

		</form>
	</div>
</body>
<script src="{{ asset('js/app.js') }}" defer></script>
<script src="{{ asset('js/survey.js') }}" defer></script>
</html>
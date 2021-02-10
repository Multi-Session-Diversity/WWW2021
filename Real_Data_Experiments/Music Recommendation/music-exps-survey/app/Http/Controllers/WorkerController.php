<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class WorkerController extends Controller
{
    public function __construct(){
	}

	public function getSurvey($workerid){
		if(!Storage::exists('input/' . $workerid . '.json'))
			abort(404);

		$contents = json_decode(Storage::get('input/' . $workerid . '.json'), true);

		foreach($contents['playlists'] as &$playlist){
			$p_total = 0;

			foreach ($playlist['sets'] as &$set) {
				$s_total = 0;
			
				foreach($set['songs'] as $song){
					$arr = explode(":", $song['duration']);
					$duration = $arr[0]*60 + $arr[1];
					$s_total += $duration;
				}
			
				$p_total += $s_total;
				$format = ($s_total >= 3600) ? 'H:i:s' : 'i:s';
				$set['duration'] = gmdate($format, $s_total);
			}
			unset($set);
			$playlist['duration'] = gmdate("H:i:s", $p_total);
		}
		unset($playlist);

		$num_playlists = end($contents['playlists'])['playlist_id'];
		$num_sets = end($contents['playlists'][0]['sets'])['set_id'];

		return view('survey', compact('contents', 'num_playlists', 'num_sets'));
	}

	public function submitSurvey(Request $request){		
		$worker_id = $request->input('worker-id');
		$context = $request->input('context');
		$amt_code = Str::random(15);
		$playlist_count = $request->input('playlist-count');
		$playlists = array();

		$info = array(
			'worker_id' => $worker_id,
			'context' => $context,
			'unique_code' => $amt_code
		);

		for($i = 1; $i <= $playlist_count; $i++) {			
			$count_selected = ($request->has(('playlist-'. $i .'-songs')) ? count($request->input('playlist-'. $i .'-songs')) : 0);
			$playlist = array(
				'playlist_id' => $i,
				'count_selected' => $count_selected,
				'count_total' => count($request->input('playlist-'. $i .'-total')),
				'artists' => (int) $request->input('playlist-'. $i .'-artists'),
				'diversity' => (int) $request->input('playlist-'. $i .'-diversity'),
				'recency' => (int) $request->input('playlist-'. $i .'-recency'),
				'familiarity' => (int) $request->input('playlist-'. $i .'-familiarity'),
				'overall' => (int) $request->input('playlist-'. $i .'-overall'),
			);

			array_push($playlists, $playlist);
		}

		$info['playlists'] = $playlists;
		$contents = json_encode($info, JSON_PRETTY_PRINT);
		Storage::put('output/'. $worker_id .'.json', $contents);
	
		return view('complete', compact('worker_id', 'amt_code'));
	}

}

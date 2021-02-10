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
		<p>Thank you for very much for completing this task, <strong>{{ $worker_id }}.</strong></p>

		<p>Your answers have been saved.</p>
        <p>Please input the following in AMT HIT.</p>

        <p class="font-weight-bold">{{ $amt_code }}</p>
    </div>
    </body>
</html>
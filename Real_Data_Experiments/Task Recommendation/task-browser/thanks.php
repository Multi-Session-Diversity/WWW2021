<?php
  $db = new PDO('sqlite:db/task_browser.db');
  // Final task button post 
  if (isset($_POST['final_finish'])){
    $session_end_time = date("Y-m-d h:i:sA");

    ######################
    // count how many windows all in all have been
    $result = $db->query("select count(*) from window;");
    foreach ($result as $result) {
      $window_count = $result['count(*)'];
    }
    // count how many sessions all in all have been
    $result = $db->query("select count(*) from session;");
    foreach ($result as $result) {
      $session_count = $result['count(*)'];
    }
    //get worker_id
    $result = $db->query("select worker_id from worker_session where session_id = $session_count;");
    foreach ($result as $result) {
      $worker_id = $result['worker_id'];
    }
    $result = $db->query("select total_reward from worker where worker_id = '$worker_id';");
    foreach ($result as $result) {
      $total_reward = $result['total_reward'];
    }

    ######################
    // update the last window time
    $window = $db->prepare("UPDATE window SET window_end_time = :window_end_time WHERE window_id = :window_id;");
    $window->execute([
      ':window_end_time' => $session_end_time,
      ':window_id' => $window_count
    ]);

    // also update the session when finish button is pressed
    $session = $db->prepare("UPDATE session SET session_end_time = :session_end_time WHERE session_id = :session_id;");
    $session->execute([
      ':session_end_time' => $session_end_time,
      ':session_id' => $session_count
    ]);

    //update worker's completion code
    $completion_code = getToken(10);
    $worker = $db->prepare("UPDATE worker SET completion_code = :completion_code WHERE worker_id = :worker_id;");
    $worker->execute([
      ':completion_code' => $completion_code,
      ':worker_id' => $worker_id
    ]);
  }
?>












<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Thanks</title>

        <link rel="stylesheet" type="text/css" href="css/mturk.css">
        <link href="https://s3.amazonaws.com/mturk-public/bs30/css/bootstrap.min.css" rel="stylesheet" />

        <script type="text/javascript" src="js/jquery-1.3.2.min.js"></script>
        <script type="text/javascript" src="js/jquery-ui-1.7.custom.min.js"></script>
        <script type="text/javascript" src="js/freewall.js"></script>
    </head>

    <body>
        <div id="page-wrap">
            <section class="container2" style="margin-bottom:15px; padding: 10px 10px; color:#333333;">
            <!-- Instructions -->
            <div class="panel panel-primary">
                <div class="panel-heading" style="font-size:13px">
                    <strong>Thank you!</strong>
                </div>
                <div id="instructions" class="panel-body" style="padding-top: 10px; padding-bottom: 5px">
                    Thank you very much for taking part in this study. 
                    <ul>
                        <li /> Your answers have been saved. 
                        <li /> Your total reward is: <b> <?php echo $total_reward . " USD."; ?> </b>
                        <li /> We will give your reward as a bonus later on.  
                        <li /> Please input the following code in the AMT HIT: <b><?php  echo $completion_code; ?></b>
                    </ul>
                </div>
            </div>
        </div>
    </body>
</html>















<?php
//reference: http://stackoverflow.com/questions/1846202/php-how-to-generate-a-random-unique-alphanumeric-string/13733588#13733588
function crypto_rand_secure( $min, $max )
{
    $range = $max - $min;
    if ($range < 1) return $min; // not so random...
    $log = ceil(log($range, 2));
    $bytes = (int) ($log / 8) + 1; // length in bytes
    $bits = (int) $log + 1; // length in bits
    $filter = (int) (1 << $bits) - 1; // set all lower bits to 1
    do {
        $rnd = hexdec(bin2hex(openssl_random_pseudo_bytes($bytes)));
        $rnd = $rnd & $filter; // discard irrelevant bits
    } while ($rnd >= $range);
    return $min + $rnd;
}

function getToken( $length )
{
    $token = "";
    $codeAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    $codeAlphabet.= "abcdefghijklmnopqrstuvwxyz";
    $codeAlphabet.= "0123456789";
    $max = strlen($codeAlphabet) - 1;

    for ($i=0; $i < $length; $i++) 
    {
        $token .= $codeAlphabet[crypto_rand_secure(0, $max)];
    }
    return $token;
}
?>



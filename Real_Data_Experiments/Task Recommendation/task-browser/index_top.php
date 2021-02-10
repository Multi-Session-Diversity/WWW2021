<?php
  $db = new PDO('sqlite:db/task_browser.db');
  $worker_id = $_REQUEST['worker_id'];
  $session_start_time = date("Y-m-d h:i:sA");

  ##############
  // count how many sessions have been
  $result = $db->query("select count(*) from session;");
  foreach ($result as $result) {
    $session_count = $result['count(*)'];
  }
  // if session is only reloaded
  $result = $db->query("select session_end_time from session where session_id = $session_count;");
  foreach ($result as $result) {
    if($result['session_end_time'] == ''){
      $session_count = $session_count-1;
    }
  }
  // count how many windows all in all have been
  $result = $db->query("select count(*) from window;");
  foreach ($result as $result) {
    $window_count = $result['count(*)'];
  }
  // if window is only reloaded
  $result = $db->query("select window_end_time from window where window_id = $window_count;");
  foreach ($result as $result) {
    if($result['window_end_time'] == ''){
      $window = $db->prepare("UPDATE window SET window_end_time = :window_end_time WHERE window_id = :window_id;");
      $window->execute([
        ':window_end_time' => $session_start_time,
        ':window_id' => $window_count
      ]);;
    }
  }

  ##############
  // insert new session_id and session_start_time
  $session = $db->prepare("INSERT INTO session (session_id, session_start_time) VALUES (:session_id, :session_start_time);");
  $session->execute([
    ':session_id' => $session_count+1,
    ':session_start_time' => $session_start_time
  ]);
  
  // insert new window_id and window_start_time
  $window = $db->prepare("INSERT INTO window (window_id, worker_id, window_start_time) VALUES (:window_id, :worker_id, :window_start_time);");
  $window->execute([
    ':window_id' => $window_count+1,
    ':worker_id' => $worker_id,
    ':window_start_time' => $session_start_time
  ]);
  
  #################  
  // insert new instance of worker_session
  $worker_session = $db->prepare("INSERT INTO worker_session VALUES (:worker_session_id, :worker_id, :session_id);");
  $worker_session->execute([
    ':worker_session_id' => NULL,
    ':worker_id' => $worker_id,
    ':session_id' => $session_count+1
  ]);
  // insert new instance of session_window
  $session_window = $db->prepare("INSERT INTO session_window VALUES (:session_window_id, :session_id, :window_id);");
  $session_window->execute([
    ':session_window_id' => NULL,
    ':session_id' => $session_count+1,
    ':window_id' => $window_count+1
  ]);
?>

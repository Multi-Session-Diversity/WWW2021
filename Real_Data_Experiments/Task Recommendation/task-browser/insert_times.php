<?php 
  //this overall updates timestamps

  $db = new PDO('sqlite:db/task_browser.db');
  $window_time = date("Y-m-d h:i:sA");

  ################
  // get row count of window
  $result = $db->query("select count(*) from window;");
  foreach ($result as $result) {
    $window_count = $result['count(*)'];
  }
  $result = $db->query("select worker_id from window where window_id = $window_count;");
  foreach ($result as $result) {
    $worker_id = $result['worker_id'];
  }
  // count how many sessions have been
  $result = $db->query("select count(*) from session;");
  foreach ($result as $result) {
    $session_count = $result['count(*)'];
  }

  ################
  //update existing window
  $window = $db->prepare("UPDATE window SET window_end_time = :window_end_time WHERE window_id = :window_id;");
  $window->execute([
    ':window_end_time' => $window_time,
    ':window_id' => $window_count
  ]);

  // create new window rows
  $window = $db->prepare("INSERT INTO window (window_id, worker_id, window_start_time) VALUES (:window_id, :worker_id, :window_start_time);");
  $window->execute([
    ':window_id' => $window_count+1,
    ':worker_id' => $worker_id,
    ':window_start_time' => $window_time
  ]);

  // insert new instance of session_window
  $session_window = $db->prepare("INSERT INTO session_window VALUES (:session_window_id, :session_id, :window_id);");
  $session_window->execute([
    ':session_window_id' => NULL,
    ':session_id' => $session_count,
	':window_id' => $window_count+1
  ]);
?>
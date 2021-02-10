<?php
	$db = new PDO('sqlite:db/task_browser.db');
	$tasks = explode("-", $_POST['task_instance_id']);

	$task_instance_id = $tasks[0] . "-" . $tasks[1] . "-" . $tasks[2];
  $task_id = $tasks[2];
  $window_id = $tasks[1];
	$worker_id = $tasks[0];
	$answer = $_POST['answer'];
	$answer_time = date("Y-m-d h:i:sA");

  $result = $db->query("select count(*) from window;");
  foreach ($result as $result) {
    $window_count = $result['count(*)'];
  }
  $result = $db->query("select total_reward from worker where worker_id='$worker_id';");
  foreach ($result as $result) {
    $total_score = $result['total_reward'] + $_POST['reward'];
  }

  ########################
  //update window time
  $window = $db->prepare("UPDATE window SET window_end_time = :window_end_time WHERE window_id = :window_id;");
  $window->execute([
    ':window_end_time' => $answer_time,
    ':window_id' => $window_id
  ]);

  // also update the worker when finish button is pressed
  $worker = $db->prepare("UPDATE worker SET total_reward = :total_reward WHERE worker_id = :worker_id;");
  $worker->execute([
    ':total_reward' => $total_score,
    ':worker_id' => $worker_id
  ]);

	$task_instance = $db->prepare("INSERT INTO task_instance VALUES (:task_instance_id, :task_id, :worker_id, :answer, :answer_time, :window_id, :quality_score);");
  $task_instance->execute([
    ':task_instance_id' => $task_instance_id,
    ':task_id' => $task_id,
    ':worker_id' => $worker_id,
    ':answer' => $answer,
    ':answer_time' => $answer_time,
    ':window_id' => $window_id,
    ':quality_score' => $_POST['reward']
  ]);
  echo "Done";
?>
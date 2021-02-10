<?php include "index_top.php"?>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Task Browser</title>

  <link rel="stylesheet" type="text/css" href="css/mturk.css">
  <link href="https://s3.amazonaws.com/mturk-public/bs30/css/bootstrap.min.css" rel="stylesheet" />

  <script type="text/javascript" src="js/jquery-1.3.2.min.js"></script>
  <script type="text/javascript" src="js/jquery-ui-1.7.custom.min.js"></script>
  <script type="text/javascript" src="js/freewall.js"></script>
  <script type="text/javascript" src="js/tasks.js"></script>

  <script type="text/javascript">
    $(function() {
      var $tabs = $('#tabs').tabs();
      $('.next-tab').click(function() { 
        $tabs.tabs('select', $(this).attr("rel"));
        $.ajax({
          type: 'POST',
          url: 'insert_times.php',
        });
        return false;
      });
    });

    $(document).ready(function(){
      $(".toggle_container").hide(); 
      $("button.reveal").click(function(){
        $(this).toggleClass("active").next().slideToggle("fast");
        if ($.trim($(this).text()) === 'Show') {
          $(this).text('Hide');
        } else {
          $(this).text('Show');        
        }
        return false; 
      });
      $("a[href='" + window.location.hash + "']").parent(".reveal").click();
    });

    $(function () {
      $('.task_finish').click(function(e) {
        e.preventDefault();
        if(typeof answer == 'undefined'){
          answer= $('input:text[name='+task_instance_id+']').attr('value');
        }
        var reward = $('input:hidden[name='+task_instance_id.slice(0, -2)+']').val();
        $.ajax({
          type: 'POST',
          url: 'insert_task_instance.php',
          data: {task_instance_id: task_instance_id, answer: answer, reward: reward}
        });
        $(this).attr("disabled", true);
        $('input[name='+task_instance_id+']').attr('disabled',true);
        return false;
      });

      var task_instance_id;
      var answer;

      // radio
      $('input:radio').click(function() { 
        task_instance_id = $(this).attr('name');
        answer = $(this).attr('value');
      });

      // text
      $('input:text').click(function() { 
        task_instance_id = $(this).attr('name');
        var answer_2;
        answer = answer_2;
      });
    });
  </script>
</head>

<body>
  <div id="page-wrap">
  <section class="container2" style="margin-bottom:15px; padding: 10px 10px; color:#333333;">
    
    <!-- Instructions -->
    <div class="panel panel-primary">
      <div class="panel-heading" style="font-size:13px"><strong>Instructions</strong>
        <button class="reveal" style="float:right" id="showIns">Show</button>
        <div id="instructions" class="toggle_container" style="padding-top: 10px; padding-bottom: 5px">
          <ul>
            <li /> In this task, you will be shown a number of different tasks organized per tab. 
            <li /> Please complete as many tasks as you want. 
            <li /> When you click on the submit button, your total reward based on the number of tasks you have completed will be completed. 
            <li /> You will then be given a unique code. Please input the code in Amazon Mechanical Turk. 
          </ul>
        </div>
      </div>
    </div>
    <!-- End Instruction -->

    <div id="tabs" style="height: 600px">
      <ul>
      <?php
        // tabber
        $filename = "input/" . $worker_id . ".tasks";
        $file = file_get_contents($filename);
        $worker = $db->prepare("INSERT INTO worker(worker_id, memo, total_reward) VALUES (:worker_id, :memo, :total_reward);");
        $worker->execute([
          ':worker_id' => $worker_id,
          ':memo' => $file,
          ':total_reward' => 0
        ]);
        $task_list = explode("\n", $file);
        $tab_count = count($task_list);

        for ($i = 1; $i < $tab_count; $i++ ){
          $task_list[$i] = trim($task_list[$i], '{}');
          echo "<li><a class=\"disabled\" href=\"#fragment-$i\">$i</a></li>";
        }
      ?> 
      </ul>
      <form action="thanks.php" method="post">
          <input type='submit' name='final_finish' value='Finish Task'/>
      </form>
      <?php
        for ($i = 1; $i < $tab_count; $i++ ){  //for each window
          echo "<div id=\"fragment-$i\" class=\"ui-tabs-panel ui-tabs-hide\">";
          echo "<div class=\"onecol\">";

          $tasks = explode(",", $task_list[$i]);
          $task_count = count($tasks);
          

          for ($j = 0; $j < $task_count; $j++){  //for each task in a window
            try{
              $query =  "select a.task_id, a.question, b.task_type_id, b.title, b.template, b.description, b.reward, b.requester, b.keywords from task a, task_type b where a.task_type_id = b.task_type_id and a.task_id =" . $tasks[$j] . ";";    
              $result = $db->query($query);

              foreach ($result as $result) {
                $template = file_get_contents($result['template']);
                $template = str_replace("\$taskNo", ($j+1) , $template);

                //write task type details
                $template = str_replace("\$title", $result['title'], $template);
                $template = str_replace("\$description", $result['description'], $template);
                $template = str_replace("\$reward", $result['reward'], $template);
                $template = str_replace("\$requester", $result['requester'], $template);
                $template = str_replace("\$keywords", $result['keywords'], $template);

                //write specific tasks
                $question_json = $result['question'];
                $question_arr = json_decode($question_json);
                $var_count = count($question_arr);

                for ($k = 0; $k < $var_count; $k++){
                  if ((strpos($question_json, 'content') !== false) and (strpos($question_json, 'label') !== false)) {
                    $template = str_replace(("$" . $question_arr[$k]->label), $question_arr[$k]->content, $template);
                  }
                  if ((strpos($question_json, 'path') !== false) and (strpos($question_json, 'label') !== false)) {
                    $template = str_replace(("$" . $question_arr[$k]->label), $question_arr[$k]->path, $template);
                  }
                }
                $tab = $window_count+$i;
                $template = str_replace("\$keywords", $result['keywords'], $template);
                $task_instance_id = $worker_id . "-" . "$tab" . "-" . $result['task_id'];
                $template = str_replace("\$task_instance_id", $task_instance_id , $template);

                $sql = "select worker_id from task_instance where task_id = " . $result['task_id'] . ";";
                $check_result = $db->query($sql);
                foreach ($check_result as $res) {
                  if ($res['worker_id'] == $worker_id) {
                    $template = "You have completed this task before.";
                  }
                }

                echo $template;
              }
              echo '<div class="divider">&nbsp;</div>';
            } catch(PDOException $e) {
              echo $e->getMessage();
            }
          }
          $next = $i+1;
          echo "</div>";
          if($next != $tab_count){
            echo "<input type=\"submit\" style=\"font-size:20px; float:right;\" class=\"next-tab mover\" rel=\"$next\" value=\"Next\"/>";
          }
          echo "</div>"; 
        }
      ?>
    </div>
  </section>   
  </div>
</body>
</html>

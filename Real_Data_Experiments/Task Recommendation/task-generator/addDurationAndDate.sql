ALTER TABLE tasktype ADD COLUMN duration int;
ALTER TABLE tasktype ADD COLUMN creation_date timestamp;

update tasktype set duration=30 where task_type_id=1;
update tasktype set duration=15 where task_type_id=2;
update tasktype set duration=40 where task_type_id=3;
update tasktype set duration=25 where task_type_id=4;
update tasktype set duration=10 where task_type_id=5;
update tasktype set duration=20 where task_type_id=6;
update tasktype set duration=15 where task_type_id=7;
update tasktype set duration=12 where task_type_id=8;
update tasktype set duration=30 where task_type_id=9;
update tasktype set duration=17 where task_type_id=10;

update tasktype set creation_date='2019/03/10 21:31' where task_type_id=1;
update tasktype set creation_date='2019/04/01 19:10' where task_type_id=2;
update tasktype set creation_date='2019/03/11 7:21' where task_type_id=3;
update tasktype set creation_date='2019/04/05 11:29' where task_type_id=4;
update tasktype set creation_date='2019/03/28 18:57' where task_type_id=5;
update tasktype set creation_date='2019/04/03 15:46' where task_type_id=6;
update tasktype set creation_date='2019/03/17 13:33' where task_type_id=7;
update tasktype set creation_date='2019/04/06 1:44' where task_type_id=8;
update tasktype set creation_date='2019/03/10 14:09' where task_type_id=9;
update tasktype set creation_date='2019/03/27 12:07' where task_type_id=10;
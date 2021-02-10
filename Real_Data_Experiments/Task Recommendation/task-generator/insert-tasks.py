task_type_id = 1

for task_id in range(1,20001):

	insert_query = "insert into task values(" + str(task_id) + ", " + str(task_type_id) + ", '[{\"content\": \"\", \"label\": \"tweet\"}]');" 
	print(insert_query)

	if ((task_id) % 2000) == 0:
		task_type_id = task_type_id + 1

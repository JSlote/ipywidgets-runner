```
def update_dag(widget_name):
	determine list of nodes_to_update by subsetting linear extension
	append nodes_to_update to end of to-do list
	remove intersection of nodes_to_update from to-do list
		if one of nodes to remove is 0th, interrupt the worker thread

worker_thread:
	while true:
		peek at next task
		if task
			do task
			pop
		else
			"sleep" until next task


class Node:
	dag = blablabla
	widget_mapping = {
		widget_name: [references to nodes that use it]
	}


	def __init__():
		ancestors = []
		go through ins:
			if input is widget
				if widget not in widget_mapping
					add widget (use widget.id())
					add observer(partial(update_dag, widget.id()))
				add self to value list for that widget
			else input is node
				append to ancestors

		add self to dag, using ancestor list

wr.start(main_widget):
	find linear extension
	kick off worker thread
	display(main_widget)
  
```

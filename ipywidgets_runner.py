import ipywidgets as w

def start(widget):
    # find linear extension
    # kick off worker thread
    # display(main_widget)
    pass

work_queue = []

def update_dag(widget_name):
    # determine list of nodes_to_update by subsetting linear extension
    # append nodes_to_update to end of to-do list
    # remove intersection of nodes_to_update from to-do list
    #     if one of nodes to remove is 0th, interrupt the worker thread
    pass

# worker_thread:
#     while true:
#         peek at next task
#         if task
#             do task
#             pop
#         else
#             "sleep" until next task

class Node:
    # DAG = BLABLA #todo network x stuff
    linear_extension = []
    widget_mapping = {}
    
    def __init__(self, args, f):
        ancestors = []
        for arg in args:
            if isinstance(arg, w.DOMWidget):
                if arg not in Node.widget_mapping:
                    Node.widget_mapping[id(arg)] = []
                    # todo add observer
                Node.widget_mapping[id(arg)].append(self)
            elif isinstance(arg, Node):
                ancestors.append(arg)
            else: raise Exception #todo pick exception
        
        Node.linear_extension.append(self)
        # DAG.add(self)
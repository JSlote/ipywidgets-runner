# todo: add kwargs to nodes
# remove need for global

import ipywidgets as w
from multiprocessing import Process

def start(widget):
    display(widget)

work_queue = []

# worker_thread:
#     while true:
#         peek at next task
#         if task
#             do task
#             pop
#         else
#             "sleep" until next task

class Output:
    """
    Container class for multi-modal node outputs
    """
    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value

class Worker:
    """
    Class to manage the worker thread
    """
    def __init__(self, work_queue):
        self.process = Process(target=self.worker_process, args=(work_queue,))

    def stop(self):
        self.process.terminate()

    def start(self):
        try:
            self.process.start()
        except AssertionError: # it's not initial, it lived and died
            self.process = Process(target=self.worker_process, args=(work_queue,))
            self.process.start()

    def worker_process(self, work_queue):
        while work_queue:
            self._run_node(work_queue[0])
            work_queue.pop(0)

    def _run_node(self, node):
        print("YEEEHAWWWW")
        if node.out:
            node.out.layout = w.Layout(border="dashed green 3px")
        args = []
        for arg_obj in node.args:
            if isinstance(arg_obj, w.DOMWidget):
                args.append(arg_obj.value)

            # if the input is a Node, add an edge
            elif isinstance(arg_obj, Node):
                args.append(arg_obj.value)

        output = node.f(*args)

        if isinstance(output, Output):
            display = output.display
            value = output.value
        else:
            display = output
            value = output


        node.value = value

        if node.out:
            node.out.clear_output()
            if isinstance(display, str):
                node.out.append_stdout(display)
            else:
                try:
                    node.out.append_display_data(display)
                except Exception as e:
                    print("Display exception for that output!", e)
                    node.out.append_stdout(display)

            node.out.layout = w.Layout(border="none")

worker = Worker(work_queue)

def handle_widget_change(change):
    widget = change.owner
    print("Updating dag")
    # determine list of nodes to update by subsetting linear extension
    direct_descendants = set(widget_descendants[id(widget)])
    stale_nodes = direct_descendants.union(all_descendants(direct_descendants))
    stale_sorted = [node for node in linear_extension if node in stale_nodes]

    for node in stale_nodes:
        if node.out:
            node.out.layout = w.Layout(border="dashed red 3px")

    print("Nodes to update:", stale_sorted)

    global work_queue

    # interrupt the worker if its workin on a stale node
    if len(work_queue) and work_queue[0] in stale_nodes:
        worker.stop()

    # remove any stale nodes from the task queue: we need to start the waterfall
    # with the new data
    work_queue = [task for task in work_queue if task not in stale_nodes]
    # put all stale nodes onto the end of the queue
    work_queue += stale_sorted

    print("Current work queue")
    print(work_queue)

    # start the worker thread again if its stopped
    worker.start()

linear_extension = []
widget_descendants = {}

def all_descendants(nodes):
    """
    Efficiently computes and returns set of all descendants of nodes

    Works by "sweeping" a row down the graph, starting with nodes, 
    then the direct descendants of all nodes, etc. etc.
    """
    all_descendants = set()

    curr_set = nodes

    while curr_set:
        new_set = set()
        for node in curr_set:
            for descendant in node.descendants:
                if descendant not in all_descendants:
                    all_descendants.add(descendant)
                    new_set.add(descendant)
        curr_set = new_set

    return all_descendants


class Node:

    def __init__(self, args=[], f=lambda *args, **kwargs: None, out=None):
        self.args = args
        self.f = f

        assert isinstance(out, w.widgets.widget_output.Output)
        self.out = out

        self.ancestors = set()
        self.descendants = set()
        self.value = None # will hold f's output'

        # tack onto growing dag
        for arg in args:
            # if the input is a widget,
            # add this Node to its list of descendants
            if isinstance(arg, w.DOMWidget):
                print("This ancestor is a widget")
                if arg not in widget_descendants:
                    widget_descendants[id(arg)] = []
                    # todo add observer
                    arg.observe(handle_widget_change, names=["value"])


                widget_descendants[id(arg)].append(self)

            # if the input is a Node, add an edge
            elif isinstance(arg, Node):
                arg.descendants.add(self)
                self.ancestors.add(arg)

            # there's an input that's not a widget or a node
            else: raise Exception #todo pick exception
        
        linear_extension.append(self)

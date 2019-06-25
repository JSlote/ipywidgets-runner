# todo: add kwargs to nodes
# remove need for global
# multiprocessing might need a multiprocessing.queue, rather than just a list.
#   problem is, I'm not sure the m.queue allows us to peak OR edit. So we'll have to figure something out.
#   in fact, multiprocessing may not work at all.

# Players in our play tonight:
# DAG composed of nodes
# stale_node_queue kept in line thanks to a linear extension (a.k.a. topological sort)
# worker process

# a node is stale if we no longer are sure its output corresponds to its input
# a node is potentially stale if it has an ancestor which is stale

# Notes about the worker
# on the one hand, threads allow us to share unpicklable stuff
# on the other hand, threads can't be killed safely
# on one foot, processes (from multiprocessing) can be safely killed
# on the other foot, processes can't share info easily
# Solution: use multiprocessing in a thread
# Thread is born when queue goes from length 0 to length > 0
# Thread dies when queue goes back to length 0
# Each f is run in a different process
# Return values are handled in thread 


import ipywidgets as w
from multiprocessing import Pool, TimeoutError
from threading import Thread

def start(widget):
    display(widget)

stale_node_queue = []

class Output:
    """
    Container class for multi-modal node outputs
    """
    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value

class Worker:
    """
    Worker manager.

    Runs in a separate thread and spawns subprocesses for each node computation
    """
    def __init__(self, stale_node_queue):
        self.stale_node_queue = stale_node_queue
        self.thread = Thread(target=self.run_thread)
        self.singleton_pool = None
        self.interrupt = False

    def run_thread(self):
        while self.stale_node_queue:
            # peek at the next node in the queue
            node = self.stale_node_queue[0]

            # let everyone know we're workin on it
            if node.out:
                node.out.layout = w.Layout(border="dashed green 3px")

            # assemble the function args
            args = []

            for arg_obj in node.args:
                # just for clarity's sake. not necessary
                if isinstance(arg_obj, w.DOMWidget):
                    args.append(arg_obj.value)
                elif isinstance(arg_obj, Node):
                    args.append(arg_obj.value)

            # start off a mini pool to run our f
            # and make it easy to get the result
            self.singleton_pool = Pool(processes=1)
            f_result = self.singleton_pool.apply_async(node.f, args)
            self.singleton_pool.close()

            # jump between waiting for the result and checking whether
            # we're supposed to cancel
            #  - if we're supposed to cancel, kill the worker, end the pool, etc.
            #  - otherwise, update everything as necessary

            done = False
            while not done:
                try:
                    output = f_result.get(timeout=0.1) # assume seconds?
                    # todo: might be able to terminate from main thread instead
                    # meaning we'd have to deal with this part differently
                except TimeoutError:
                    pass
                else:
                    done = True
                if self.interrupt:
                    # print("BAILIN'", flush=True)
                    self.singleton_pool.terminate()
                    self.singleton_pool.join()
                    self.interrupt = False
                    return # bail

            # handle outputs
            if isinstance(output, Output):
                display = output.display
                value = output.value
            else:
                display = output
                value = output

            # update the value for the node
            node.value = value

            # if we're supposed to be writing to an output widget
            if node.out:
                node.out.clear_output()
                if isinstance(display, str):
                    node.out.append_stdout(display)
                else:
                    try:
                        node.out.append_display_data(display)
                    except Exception as e:
                        # print("Display exception for that output!", e, flush=True)
                        node.out.append_stdout(display)

                node.out.layout = w.Layout(border="none")

            self.stale_node_queue.pop(0)
            # print("Queue:", self.stale_node_queue, " - end of running a node", flush=True)

        # if we get here, we've run through everything in the queue

    def stop(self):
        self.interrupt = True
        if self.singleton_pool:
            self.singleton_pool.join()

    def start(self):
        # if the thread is waiting to start
        # start it
        # otherwise make a new thread

        try:
            self.thread.start()
            # print("start success", flush=True)
        except RuntimeError: # it's not initial, it lived and died
            self.thread = Thread(target=self.run_thread)
            self.thread.start()
            # print("had to make a new one, but started successfully", flush=True)

worker = Worker(stale_node_queue)

def handle_widget_change(change):
    widget = change.owner
    # print("Updating dag", flush=True)
    # determine list of nodes to update by subsetting linear extension
    direct_descendants = set(widget_descendants[id(widget)])
    new_stale_nodes = direct_descendants.union(all_descendants(direct_descendants))
    new_stale_nodes_sorted = [node for node in linear_extension if node in new_stale_nodes]

    for node in new_stale_nodes:
        if node.out:
            node.out.layout = w.Layout(border="dashed red 3px")

    global stale_node_queue

    # interrupt the worker if its workin on a stale node
    if len(stale_node_queue) and stale_node_queue[0] in new_stale_nodes:
        worker.stop()

    # remove any stale nodes from the node queue: we need to start the waterfall
    # with the new data
    for i, node in enumerate(stale_node_queue):
        if node in new_stale_nodes:
            stale_node_queue.pop(i)

    # put all stale nodes onto the end of the queue
    # stale_node_queue += new_stale_nodes_sorted
    stale_node_queue += new_stale_nodes_sorted


    # print("Queue:", stale_node_queue, " - end of handler", flush=True)

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

        if out:
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
                # print("This ancestor is a widget", flush=True)
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

# todo: add kwargs to nodes
# remove need for global
# right now the worker owns the stale_node_queue. Is that correct?

# Players in our show tonight:
#
# DAG composed of nodes
# stale_node_queue kept in line thanks to a linear extension (a.k.a. topological sort)
# worker process consuming from the queue

# a node is stale if we no longer are sure its output corresponds to its input (though it might if f is not injective)
# a node is potentially stale if it has an ancestor which is stale

import ipywidgets as w
from multiprocessing import Pool, TimeoutError
import threading as th

def pp_queue(queue):
    out = ""
    if queue:
        for el in queue:
            out += " - "+str(id(el))+"\n"
    return out[:-2]

the_output = w.Output()

def start(widget):
    global the_output
    total = w.HBox([widget, the_output])
    display(total)

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

    Runs a thread that spawns subprocesses (well, pools) for each node computation.
    Can be interrupted.
    """
    def __init__(self):
        self.stale_node_queue = []
        self.consumer_thread = th.Thread(target=self.consume)
        self.queue_condition = th.Condition()
        self.singleton_pool = None
        self.interrupted = False
        self.curr_node = None # to hold the current node being worked on

        self.consumer_thread.start()


    def consume(self):
        global the_output
        with the_output:
            print("Thread running", flush=True)
        while True:
            with the_output:
                print("\nTop of the loop.\nAttempting consume; queue:\n", pp_queue(self.stale_node_queue), flush=True)

            # acquire the lock, grab a thingy when possible
            with self.queue_condition:
                while not self.stale_node_queue:

                    with the_output:
                        print("Waiting for something to be in the queue", flush=True)

                    self.queue_condition.wait()

                    with the_output:
                        print("\n\nI'm told there's something in the queue", flush=True)

                with the_output:
                    print("Consuming from the queue:\n", pp_queue (self.stale_node_queue), flush=True)

                self.curr_node = self.stale_node_queue.pop(0)

            # lock released

            # display that we're working on it
            if self.curr_node.out:
                self.curr_node.out.layout = w.Layout(border="dashed green 3px")

            # assemble the function args
            # args = []

            # for arg_obj in self.curr_node.args:
            #     # just for clarity's sake. not necessary
            #     if isinstance(arg_obj, w.DOMWidget):
            #         args.append(arg_obj.value)
            #     elif isinstance(arg_obj, Node):
            #         args.append(arg_obj.value)

            args = [arg.value for arg in self.curr_node.args]

            # start off a mini pool to run our f
            # and make it easy to get the result
            self.singleton_pool = Pool(processes=1)
            f_pending_return_value = self.singleton_pool.apply_async(self.curr_node.f, args)
            self.singleton_pool.close()

            # jump between waiting for the result and checking whether
            # we're supposed to cancel
            #  - if we're supposed to cancel, kill the worker, end the pool, etc.
            #  - otherwise, update everything as necessary
            with the_output:
                print("\nRunning node", self.curr_node, flush=True)

            f_return_value = None
            while not f_return_value:
                try:
                    f_return_value = f_pending_return_value.get(timeout=0.1) # assume seconds?
                    # todo: might be able to terminate from main thread instead
                    # meaning we'd have to deal with this part differently
                except TimeoutError: # this is ok, just haven't finished yet
                    pass
                # else:
                #     break # we got our output!

                if self.interrupted:
                    with the_output:
                        print("INTERRUPTED!", flush=True)
                    break

            if self.interrupted:
                # reset our interrupted flag
                self.interrupted = False
                # no more current node
                self.curr_node = None
                # terminate our pool
                self.singleton_pool.terminate()
                # join it to make sure it ded
                self.singleton_pool.join()
                continue

            with the_output:
                print("got output", f_return_value, "\n", flush=True)

            # handle outputs
            if isinstance(f_return_value, Output):
                display = f_return_value.display
                value = f_return_value.value
            else:
                display = f_return_value
                value = f_return_value

            # update the value for the self.curr_node
            self.curr_node.value = value

            # if we're supposed to be writing to an output widget
            if self.curr_node.out:
                self.curr_node.out.layout = w.Layout(border="solid 3px rgba(0,0,0,0)")
                self.curr_node.out.clear_output()

                if isinstance(display, str):
                    self.curr_node.out.append_stdout(display)
                else:
                    try:
                        self.curr_node.out.append_display_data(display)
                    except Exception as e:
                        # print("Display exception for that output!", e, flush=True)
                        self.curr_node.out.append_stdout(display)

            self.curr_node = None

        # if we get here, we've run through everything in the queue


    def interrupt(self):
        self.interrupted = True
        if self.singleton_pool:
            self.singleton_pool.join()

worker = Worker()

def handle_widget_change(change):
    widget = change.owner
    # determine list of nodes to update by subsetting linear extension
    direct_descendants = set(widget_descendants[id(widget)])

    new_stale_nodes = direct_descendants.union(all_descendants(direct_descendants))
    new_stale_nodes_sorted = [node for node in linear_extension if node in new_stale_nodes]

    # show outputs as stale
    for node in new_stale_nodes:
        if node.out:
            node.out.layout = w.Layout(border="dashed gray 3px")

    # grab the queue lock
    with worker.queue_condition:
        # interrupt the worker if its working on a stale node
        if worker.curr_node in new_stale_nodes:
            worker.interrupt()
        # because we've acquired the queue lock, the worker won't be able to
        # do anything until we release the lock. So we're free to make our modifications in peace

        # remove any stale nodes from the node queue: we need to start the waterfall
        # with the new data
        worker.stale_node_queue = [node for node in worker.stale_node_queue if node not in new_stale_nodes]

        # put all stale nodes onto the end of the queue
        worker.stale_node_queue += new_stale_nodes_sorted

        # let the worker know we're done
        worker.queue_condition.notify()

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
            out.layout = w.Layout(border="solid 3px rgba(0,0,0,0)")
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

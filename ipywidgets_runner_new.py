import threading as th
import ipywidgets as w
import multiprocessing as mp

from enum import Enum


class Output:
    """
    Container class for multi-modal node outputs
    """

    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value


class Pending:
    pass


class Supervisor:

    def __init__(self):

        # the "queue" to consume from
        self.ready_nodes = set()
        self.ready_nodes_cond = th.Condition()

        self.work_lock = th.Lock()

        # node ids to workers
        self.work = {}


    def handle_node_to_ready(self, node):
        """The node is ready for a new computation"""

        with self.ready_nodes_cond:
            self.ready_nodes.add(node)
            self.ready_nodes_cond.notify()

    def handle_node_away_from_ready(self, node):
        """If node reverts to a non-ready state,
        cancel all worker-related activity for that node"""

        # check if ready for computation
        with self.ready_nodes_cond:
            if node in self.ready_nodes:
                self.ready_nodes.remove(node)
                return

        # check if needs to be interrupted
        with self.work_lock:
            if node in self.work:
                print("Interrupting worker")
                # interrupt worker at self.work[id(node)]
                del self.work[id(node)]

    def register_worker(worker):

        self.worker = worker

    def run():

        while True:

            with self.set_condition:

                while not ready_nodes:

                    self.set_condition.wait()

                ready_node = self.ready_nodes.pop()

                self.singleton_pool = mp.Pool(processes=1)
                f_pending_return_value = self.singleton_pool.apply_async(
                    ready_node.f, [arg.value for arg in ready_node.args])
                self.singleton_pool.close()


supervisor = Supervisor()


class Worker:

    def __init__(self):
        supervisor.register_worker(self)
        self.consumer_thread = th.Thread(target=self.consume)
        self.consumer_thread.start()
        

    def consume(self):

        while True:

            with supervisor.ready_nodes_cond:

                while not supervisor.ready_nodes:

                    self.ready_nodes_cond.wait()

                node = supervisor.ready_nodes.pop()

                supervisor.work[id(node)] = "poop"

                output = node.f(node.args)

                print(output, flush=True)

                node.handle_computation_end(output)

                del supervisor.work[id(node)]


class Node:
    class State(Enum):
        DONE = 0
        PENDING = 1
        READY = 2

    def __init__(self, args=None, f=lambda: None, display=None):
        for arg in args:
            if isinstance(arg, Node):
                # subscribe to traitlet
                arg.register_children(self)
            elif isinstance(arg, w.DOMWidget):
                # subscribe to traitlet
                pass
            else:
                raise Exception

        self.args = args
        self.f = f
        if display:
            assert isinstance(display, w.widgets.widget_output.Output)
            # display.layout = w.Layout(border="solid 3px rgba(0,0,0,0)")
        self.display = display
        # current inputs given by [arg.value for arg in args]
        self.old_inputs = [arg.value for arg in args]
        self.old_value = None
        self.value = None
        self.lock = th.Lock()
        self.children = set()

    def handle_parent_update(self, parent, value):
        with self.lock:
            # interrupt computation if it's happening

            # recompute state of current node
            current_inputs = [arg.value for arg in self.args]
            if Pending not in current_inputs:
                if current_inputs == self.old_inputs:
                    self.value = self.old_value
                    self.state = Node.State.DONE
                    supervisor.handle_node_away_from_ready(self)
                else:
                    self.value = Pending
                    self.state = Node.State.READY
                    supervisor.handle_node_to_ready(self)

            else:
                self.value = Pending
                self.state = Node.State.PENDING
                supervisor.handle_node_away_from_ready(self)

    def handle_computation_end(self, value):
        print(value, flush=True)
        if isinstance(value, Output):
                display = f_return_value.display
                value = f_return_value.value
        else:
            display = f_return_value
            value = f_return_value

        with self.lock:
            self.value = value
            self.state = Node.State.DONE

        if self.display:
            # self.display.layout = w.Layout(border="solid 3px rgba(0,0,0,0)")
            self.display.clear_output()

            if isinstance(display, str):
                self.display.append_stdout(display)
            else:
                try:
                    self.display.append_display_data(display)
                except Exception as e:
                    # print("Display exception for that output!", e, flush=True)
                    self.display.append_stdout(display)

    def register_children(self, node):

        self.children.add(node)


if __name__ == '__main__':

    node1 = Node(args=[], f=lambda x: 'poop again')

    node2 = Node(args=[node1], f=lambda x: 'poop')

    node2.handle_parent_update(node1, 1)




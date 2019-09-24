from ipywidgets_runner.utils import dprint
from ipywidgets_runner.worker import Worker
import threading as th

class Supervisor:

    def __init__(self):
        
        # the "queue" to consume from
        self.ready_nodes = set()
        
        # condition to notify connsumers
        self.ready_nodes_cond = th.Condition()

        self.work_lock = th.Lock()

        # node ids to workers
        self.work = {}
        
        self.start_worker_threads()


    def handle_node_to_ready(self, node):
        """The node is ready for a new computation"""

        with self.ready_nodes_cond:
            self.ready_nodes.add(node)
            self.ready_nodes_cond.notify()

    def handle_node_from_ready(self, node):
        """If node is coming from a ready state,
        there might be a worker on it. Cancel all node-related activity"""

        dprint("Canceling work...")
        
        # check if was ready for computation
        with self.ready_nodes_cond:
            dprint("  ready_nodes lock obtained...")
            if node in self.ready_nodes:
                dprint("  Node discovered in ready_nodes; deleting.")
                self.ready_nodes.remove(node)
                return

            # check if needs to be interrupted
            with self.work_lock:
                dprint("  Work lock obtained")
                if node in self.work:
                    dprint("  Node discovered in work set; interrupting and deleting.")
                    curr_worker = self.work[id(node)]
                    curr_worker.interrupt()
                    del self.work[id(node)]

    def start_worker_threads(self):
        """Start worker threads which will consume from ready node set"""
        worker_1 = Worker(self)
        worker_2 = Worker(self)
        dprint("Worker 1:", id(worker_1))
        dprint("Worker 2:", id(worker_2))
        self.workers = {worker_1, worker_2}
        
    def get_work(self, worker):
         with self.ready_nodes_cond:
            # Wait until there's a ready node available.
            # When there is, lock the ready nodes set
            # and move the node to the work dict

            while not self.ready_nodes:
                self.ready_nodes_cond.wait()

            # pop a ready node
            node = self.ready_nodes.pop()

            self.work[id(node)] = worker
            
            return node
                
    def return_work(self, worker, node, output):
        with self.work_lock:
            if self.work[id(node)] == worker:
                del self.work[id(node)]

            else:
                return
        
        node.handle_computation_end(output)

theSupervisor = Supervisor()
import threading as th

from ipywidgets_runner.utils import dprint

class Worker:

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.consumer_thread = th.Thread(target=self.consume)
        self.consumer_thread.start()
        self.stale = False
        
    def interrupt(self):
        self.stale = True
        dprint("Worker", id(self), "has become stale")

    def consume(self):
        """Consume tasks forever"""

        while True:
            
            # wait for work--blocks thread until there's something to work on
            node = self.supervisor.get_work(self)
            
            dprint("Worker", id(self), "picked up task from node", id(node))

            # straight-up run the function--in the future we'll subprocessify this
            inputs = [arg.value for arg in node.args]
            output = node.f(*inputs)
            
            if self.stale:
                dprint("Result from worker", id(self), "discarded due to staleness")
                self.stale = False
                continue
            else:
                dprint("Result from worker", id(self), "returned")
                self.supervisor.return_work(self, node, output)
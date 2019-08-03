import threading as th
import ipywidges as w
import multiprocessing as mp

class Output:
    """
    Container class for multi-modal node outputs
    """
    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value

class Pending:
	pass

class Node:
	class State(Enum):
		DONE = 0
		PENDING = 1
		READY = 2

	def __init__(self, args=None, f=lambda :None, display=None):
		for arg in args:
			if isinstance(arg, Node):
				# subscribe to traitlet
			elif isinstance(arg, w.DOMWidget):
				# subscribe to traitlet
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

	def handle_parent_update(parent, value):
		with self.lock:
			# interrupt computation if it's happening
			current_inputs = [arg.value for arg in self.args]
			if Pending not in current_inputs:
				if current_inputs == self.old_inputs:
					self.value = self.old_value
					self.state = Node.State.DONE
				else:
					self.value = Pending
					self.state = Node.State.READY
			else:
				self.value = Pending
				self.state = Node.State.PENDING

	def handle_computation(value):
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


class Worker:

	def __init__(ready_nodes=None):

		if not ready_nodes:
			self.ready_nodes = set()
		else:
			self.ready_nodes = ready_nodes

		self.set_condition = th.Condition()

		self.computations = {}

	def run():

		while True:

			with self.set_condition:

				while not ready_nodes:

					self.set_condition.wait()

				ready_node = self.ready_nodes.pop()

				self.singleton_pool = Pool(processes=1)
	            f_pending_return_value = self.singleton_pool.apply_async(ready_node.f, [arg.value for arg in ready_node.args])
	            self.singleton_pool.close()







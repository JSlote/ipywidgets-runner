import threading as th

# The players in tonight's charade
# - a dag full of nodes which are pending and/or stale
# - a job runner which manages worker threads that compute stale non-pending nodes

class DAG:
	self.stale = set()
	self.stale_prop = th.Prop()

	self.pending = set()
	self.pending_lock = th.Lock()

	self.widget_children = {}

	def handle_widget_change(self.change):
		"""
		Update the list of stale nodes based on a new value from a widget and 
		interrupt computations as necessary.
		"""
		widget = change.owner

		with self.stale_prop:
			prev_stale = self.stale
			curr_stale = set()

			# STEP 1: Update the set of stale nodes

			# First consider the nodes which were already stale and which are not 
			# children of the changed widget. These nodes are definitely still stale:
			# they aren't involved in the change.
			unchanged_stale = prev_stale.difference(self.widget_children[widget])

			# Now we consider the children of widget (some of whom could also be in
			# prev_stale).

			# There are three sorts of nodes here:
			# 	1. Nodes going from fresh to stale. We'll call them new_stale, and they
			#      are exactly children(widget) - prev_stale
			# 	2. Nodes going from stale to fresh, in the case the only input making
			# 	   the node stale was the widget's input.
			# 	3. Node going from stale to stale, in the case some other input is 
			# 	   making the node stale. We'll call them changed_stale.
			#
			# Note that in either of cases (2) or (3) if worker is current working on
			# computing f for the previous set of inputs it should be halted. Moreover,
			# together, cases (2) and (3) make up
			# prev_stale.intersection(children(widget)), which we'll call
			# changed_prev_stale.

			new_stale = self.widget_children[widget].difference(prev_stale)
			changed_stale = set()

			changed_prev_stale = prev_stale.difference(self.widget_children[widget])

			for node in changed_prev_stale
				if node.is_stale(): # still stale--meaning the inputs have changed!
					changed_stale.add(node)
				# else node was stale but not stale any longer!

			self.stale = unchanged_stale.union(changed_stale).union(new_stale)

			# STEP 2: Determine what nodes are pending
			with self.pending_lock:
				self.pending = all_descendants(stale)
			# To-do: is there a more efficient way to compute all descendants than
			# recomputing every time?

			# STEP 3: Interrupt workers who are behind the times
			should_interrupt = self.pending.union(changed_prev_stale, pending)

			JobRunner.interrupt_on_nodes(should_interrupt)

			# STEP 4: # if there are in fact stale nodes, let it be known to the world!
			if self.stale:
				stale_prop.notify()

	def update_node_output(self, node, value):
		# a stale node is now fresh
		# for each child, check whether they're stale and not pending and, if so,
		# add to stale!

		node.update_output(new_value)

		with stale_prop:
			self.stale.remove(node)

			for child in node.children:
				child.update_input(parent=node, value=value)

			# we have to do these separately because you can have a child of
			# a child (I know, I know, quite incestuous)

			for child in node.children:
				# determine if node is stale
				if child.is_stale() and not child.is_pending():
					self.stale.add(child)


class JobRunner:
	"""
	Manages workers and tracks the subset of stale nodes being worked on at any
	given point of time.
	"""
	def __init__(self):
		self.working_set = set()
		self.working_set_lock = th.Lock()

		# TODO: instantiate some number of threads

	def request_node(self):
		"""
		Provide a (guaranteed stale) node to compute, otherwise block until there is one. Used by
		workers.
		"""
		with DAG.stale_prop:
			# block until there's a stale node
			while not DAG.stale:
				stale_prop.wait()

			# TODO: verify this is more efficient than sampling
			# stale - pending - working_set
			for node in DAG.stale.difference(DAG.pending):
				if node not in self.working_set:
					with self.working_set_lock:
						self.working_set.add(node)
					return node

	def return_node(self, node, new_value):
		with self.working_set_lock:
			self.working_set.remove(node)

		dag.update_node(node, value)

	def interrupt_on_nodes(self, nodes):
		for node in intersection(nodes, self.working_set.keys()):
			self.working_set[node].interrupt()
			with self.working_set_lock:
				self.working_set.remove(node)

class Node:
	def __init__(self):
		self.computed_in = { id(parent) : parent.value for parent in parents }
		self.value = None

	def update_input(self, parent, value):
		pass

	def is_stale(self):
		

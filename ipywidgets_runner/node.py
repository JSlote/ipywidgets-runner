from enum import Enum
import traitlets as tr
import ipywidgets as w
from ipywidgets_runner.utils import dprint, Pending, Output
from ipywidgets_runner.supervisor import theSupervisor

class Node(tr.HasTraits):
    
    value = tr.Any()
    
    @tr.default("value")
    def _set_default_value(self):
        return Pending
    
    class State(Enum):
        DONE = 0
        PENDING = 1
        READY = 2

    def __init__(self, args=None, f=lambda: None, display_widget=None):
        dprint("Created Node with ID", id(self))
        for arg in args:
            if isinstance(arg, Node):
                # subscribe to traitlet
                arg.observe(self.handle_parent_change, names=["value"])
            elif isinstance(arg, w.DOMWidget):
                # subscribe to traitlet
                arg.observe(self.handle_parent_change, names=["value"])
            else:
                raise Exception

        self.args = args
        self.f = f
        
        if display_widget:
            assert isinstance(display_widget, w.widgets.widget_output.Output)
            
        self.display_widget = display_widget
        # current inputs given by [arg.value for arg in args]
        self.old_inputs = [arg.value for arg in args]
        self.old_value = None
        self.state = Node.State.DONE
        
    def handle_parent_change(self, change):
#         # Todo: use these to speed up comparison of current inputs to old_inputs
#         parent = change.owner
#         p_value = parent.value
        
        current_inputs = [arg.value for arg in self.args]

        # State machine
        #                    : on node(+ state upd8) : on supervisor
        #
        # ready   -> ready   : do nothing            : cancel and then add
        # ready   -> done    : value <- old_value    : cancel
        # done    -> ready   : value <- pending      : add to ready
        
        # pending -> ready   : do nothing            : add to ready
        # pending -> done    : value <- old_value    : do nothing
        
        # Partial summary:
        # if from ready, call handle node away from ready
        
        # if to ready, call handle node to ready and set to pending
        # if to done, set value <- old_value
        
        
        # ready   -> pending : do nothing            : cancel
        # done    -> pending : value <- pending      : do nothing
        # pending -> pending : do nothing            : do nothing
        
        # from READY
        if self.state == Node.State.READY:        
            theSupervisor.handle_node_from_ready(self)
            
        # Case to DONE or 
        # Case to READY
        if Pending not in current_inputs:                
            # to READY
            if not current_inputs == self.old_inputs:
                theSupervisor.handle_node_to_ready(self)
                self.value = Pending
                self.state = Node.State.READY
                
            # to DONE
            else:
                self.value = self.old_value
                self.state = Node.State.DONE
                
        # Case to PENDING
        else:                
            # in any case, make sure we're pending                
            self.value = Pending
            self.state = Node.State.PENDING

    def handle_computation_end(self, value):
        """Update new and old values, draw as needed"""
        # todo--only erase and redraw when output is actually different
        if isinstance(value, Output):
            display_value = value.display
            value = value.value
            
        else:
            display_value = value
            value = value

        self.value = value
        self.state = Node.State.DONE
        
        # todo: update the old values
        # Question: can we guarantee this only gets called by "good" updates?
        
        if self.display_widget:
            self.display_widget.clear_output()

            if isinstance(display_value, str):
                self.display_widget.append_stdout(display_value)
            else:
                try:
                    self.display_widget.append_display_data(display_value)
                except Exception as e:
                    self.display_widget.append_stdout(display_value)
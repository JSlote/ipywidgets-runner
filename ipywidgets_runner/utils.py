import ipywidgets as w
import traitlets as tr

debug_output_widget = w.Output(layout=w.Layout(border='solid'))
debug_clear_button = w.Button(description="clear debug")
debug_clear_button.on_click(lambda self: debug_output_widget.clear_output())

def dprint(*args, **kwargs):
    with debug_output_widget:
        print(*args, **kwargs, flush=True)

class Pending: pass

class Output:
    """
    Container class for multi-modal node outputs
    """

    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value
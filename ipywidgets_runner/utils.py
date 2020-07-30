import ipywidgets as w
import traitlets as tr

debug_output_widget = w.Output()
debug_clear_button = w.Button(description="clear debug")
debug_clear_button.on_click(lambda self: debug_output_widget.clear_output())
debug_panel = w.VBox([debug_output_widget, debug_clear_button], layout=w.Layout(border='1px solid black'))

# def dprint(*args, **kwargs):
#     with debug_output_widget:
#         print(*args, **kwargs, flush=True)

# def dprint(*args):
#     args = [str(arg) for arg in args]
#     msg = " ".join(args)+"\n"
#     debug_output_widget.append_stdout(msg)
    
def dprint(*args, **kwargs):
    pass

class Pending: pass

class Output:
    """
    Container class for multi-modal node outputs
    """

    def __init__(self, value=None, display=None):
        self.display = display
        self.value = value
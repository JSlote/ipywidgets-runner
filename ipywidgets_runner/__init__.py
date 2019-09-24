import ipywidgets as w

from ipywidgets_runner.utils import Output
from ipywidgets_runner.utils import debug_output_widget, debug_clear_button
from ipywidgets_runner.node import Node

__display = display

def display(mainWidget, debug=False):
	if debug:
		outerWidget = w.VBox([mainWidget,
			debug_output_widget, debug_clear_button])
		__display(outerWidget)

	else:
		__display(mainWidget)

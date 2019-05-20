# ipywidgets-runner
A framework for intelligently and asynchronously scheduling ipywidgets re-renders

The `ipywidgets` library adds a powerful controls layer to Jupyter notebooks.
However, for complex visualizations requiring long-running computations dependent on a number of variables, the path to a useable interface lengthens significantly.

In these circumstances, the data scientist wants their computations to be interrupted when a parameter is changed in the configuration interface.
Furthernore, in an ideal world, only the portions of the computation actually dependent on this variable should be interrupted and recomputed.

This is `ipywidgets-runner` comes in: the data scientist specifies the computation behind a visualization as a directed acyclic graph, and `ipywidgets-runner` automatically interrupts, restarts, and schedules pieces of the computation as necessarily.

```python
import ipywidgets as w
import ipywidgets_runner as wr

first_name_widget = w.Text()
last_name_widget = w.Text()
age_widget = w.Date()

full_name_node = wr.Node(
  in=[first_name_widget, last_name_widget],
  f=lambda x, y: x+y
)
  
b = wr.Node(
  in=[a, age_widget],
  f=lambda x, y: x + str(datetime.now()-y)
)
```

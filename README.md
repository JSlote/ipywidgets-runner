# ipywidgets-runner
### Supercharge your ipywidgets dashboards and apps in Jupyter

`ipywidgets-runner` is a framework for writing ipywidget apps that include long-running computations, such as database queries or complicated statistical analyses.
When a widget value is changes, `ipywidgets-runner` intelligently schedules partial recomputations to greatly speed up tool performance.

With `ipywidgets-runner` an analysis is split up into functional components (nodes), each which depend on various widget values.
When a widget value is update, `ipywidgets-runner` will intelligently recompute only the portion of the analysis that truly depends on that parameter.

It's very easy to integrate `ipywidgets-runner` into your existing data analysis.

1. Data analysis typically takes the form of one big function _f_ which maps parameters to an collection of outputs, such as tables, charts, maps, or images.
The first step is to split this functino _f_ into a collection of smaller, interdependent functions.

2. Express the interdependence of these functions by linking them up in ipywidgets-runner _nodes_.

3. 


## Example


Just split your data analysis into seprate functions based on the parameters they depend on, link them up to each other, and 

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
output_widget = w.Output()

full_name_node = wr.Node(
  in=[first_name_widget, last_name_widget],
  f=lambda x, y: x+y
)
  
name_and_time_node = wr.Node(
  in=[full_name_node, age_widget],
  f=lambda x, y: x + str(datetime.now()-y)
)

output_node = wr.OutNode(
  in=[name_and_time_node],
  f=lambda x: plot(x),
  out=output_widget
)

container_widget = w.VBox([first_name_widget, last_name_widget, age_widget, output_widget])

wr.start(container_widget)
```

## To do
- add disk caching
- compute independent stale nodes in parallel
- add border to the layout instead of replacing it

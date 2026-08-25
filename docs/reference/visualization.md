# Visualization

Matplotlib is optional and imported only when one of these functions is called. Install the `viz` extra or synchronize all development extras.

`plot_partition` is a geometric view and therefore accepts only effective rank
one or two. For higher rank, `plot_summary` uses a projection-free retained-
eigenvalue spectrum, and `plot_optimization` summarizes center displacement
norms across every informative coordinate.

::: scorequant.plot_optimization

::: scorequant.plot_partition

::: scorequant.plot_information

::: scorequant.plot_summary

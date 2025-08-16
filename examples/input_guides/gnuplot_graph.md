# Create a graph in a Picker using gnuplot

Ensure that gnuplot is installed and then run:

```bash
listpick -i ./examples/input_files/polynomials.tsv
```

Select two columns of cells that you want to plot and then hit |.

Type or paste the following into the pipe input field:

```gnuplot -p -e 'plot "/dev/stdin" with lines'```

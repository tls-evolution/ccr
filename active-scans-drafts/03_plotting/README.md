# README plotting

This directory contains the scripts for the plotting of the results.
It also contains the scripts for the final aggregation of results prior to
plotting: Different zones are aggregated to interesting lists and the results
of single AS numbers are aggregated to one result for the corresponding big AS.

The directory `paper_results` contains the aggregrated results used for our
CCR paper. It also contains the plots (`pdf`-files) and corresponding
statistics (`.out`-files) for your convenience.
To regenerate the plots and statistics based on the aggregated results, run the
following commands:
```bash
ln -s paper_results/data data
ln -s paper_results/data_AS data_AS
./03_plot_all.sh
./04_get_share_for_AS.sh | tee 04_get_share_for_AS.out
./05_get_stats_lists.sh | tee 05_get_stats_lists.out
```

To plot data that you generated with the scripts in `../02_postprocessing`,
run the scripts in this directory in the order as indicated by their numbering.


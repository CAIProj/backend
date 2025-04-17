# backend

## Curve-smoothing Algorithms

-   Utilising mathematical algorithms to smooth a noisy curve.
-   They are
    -   Spline Fit (scipy)
    -   Loess-v1
    -   Loess-v2

-   To test locally;
    -   Clone the repository
    -   install `numpy` and `scipy` packages
    -   from `curve_smoothing` folder open the terminal
    -   run `python -m test.loess_vs_spline` or `python -m test.test_loess_v2` or other files
    -   Read/run the `curve_smoothing_algo.ipynb` to learn more about the algorithms


## gpx_dataengine

-   Retrieve Latitiude, Longitude, Altitude from a GPX file
-   Retrieve `MSL(Mean Sea Level)` Altitude
-   Compare gpx altitude and `open-elevation` online library's altitude
-   Plot and compare unparalleled gpx file
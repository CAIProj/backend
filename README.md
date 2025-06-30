# 📍 Tracking App – Backend

## 🔧 Setting Up the Python Environment Locally

1. **Clone the repository** to your local machine.
   ```sh
   git clone https://github.com/CAIProj/backend.git
   ```
2. **Navigate to the cloned directory**.
   ```sh
   cd backend
   ```
3. **Install dependencies**.

   Using [Poetry](https://python-poetry.org/):
   ```sh
   pip install poetry
   poetry install --no-root
   ```
   or using requirements.txt with pip:
   ```sh
   pip install -r requirements.txt
   ```


## Curve-smoothing Algorithms

-   Utilising mathematical algorithms to smooth a noisy curve.
-   They are
    -   Spline Fit (scipy)
    -   Loess-v1
    -   Loess-v2
    -   Savitzky-Golay Filter

-   To test locally;
    -   Set up the python environment as described above
    -   Open the terminal in `curve_smoothing` folder
    -   run `python -m test.loess_vs_spline` or `python -m test.test_loess_v2` or other files
    -   Read/run the `curve_smoothing_algo.ipynb` to learn more about the algorithms


## gpx_dataengine

-   Retrieve Latitiude, Longitude, Altitude from a GPX file
-   Retrieve `MSL(Mean Sea Level)` Altitude
-   Compare gpx altitude and `open-elevation` online library's altitude
-   Plot and compare unparalleled gpx file
-   The distance between two geographic coordinates is calculated using the Haversine formula, assuming the Earth's radius is 6371.0 km.

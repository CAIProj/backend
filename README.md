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

## Curve-Smoothing Algorithms

Utilises mathematical algorithms to smooth noisy elevation data.

### Included Algorithms

- Spline Fit (via `scipy`)
- Loess-v1
- Loess-v2

### Running the Demos Locally

1. **Set up the Python environment** as described above.
2. **From backend repo run one of the test modules like this**:
   ```sh
   python -m test.curve_smoothing.test_loess_v1
   python -m test.curve_smoothing.test_loess_v2
   python -m test.curve_smoothing.test_spline_fit
   python -m test.curve_smoothing.loessv1_vs_loessv2
   python -m test.curve_smoothing.loess_vs_spline
   ```
3. **(Optional)** Open the notebook for an algorithm walkthrough:
   ```sh
   notebooks\curve_smoothing_algo.ipynb
   ```


## GPX Track Processing and Elevation Analysis

- Load latitude, longitude, and altitude from a GPX file using `Track.from_gpx_file()`
- Retrieve a new track with altitude data from online APIs using `track.with_api_elevations()`
- Generate a new track with smoothed elevation using `track.with_smoothed_elevations()`
- Perform simple comparisons using the `Plotter` class, and synchronized comparisons using the `SynchronizedElevationPlotter` class
- Distances between geographic coordinates are calculated using the Haversine formula, assuming the Earth's radius is 6371.0 km

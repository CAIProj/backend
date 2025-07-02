# 📍 Tracking App – Backend

This backend provides tools for analyzing GPX tracks, smoothing elevation data, and comparing different elevation sources.

---

## 🚀 Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/CAIProj/backend.git
cd backend
```

### 2. Install Dependencies

#### Using [Poetry](https://python-poetry.org/)
```sh
pip install poetry
poetry install --no-root
```

#### Or using `requirements.txt` with pip
```sh
pip install -r requirements.txt
```

---

## 📈 Curve Smoothing Algorithms

Mathematical methods are used to smooth noisy elevation curves for improved comparison and visualization.

### Supported Algorithms

- **Spline Fit** (via `scipy`)
- **Loess-v1**
- **Loess-v2**

### How to Run Demos

1. Ensure your environment is set up as described above.
2. From the project root, run any of the test modules:
   ```sh
   python -m test.curve_smoothing.test_loess_v1
   python -m test.curve_smoothing.test_loess_v2
   python -m test.curve_smoothing.test_spline_fit
   python -m test.curve_smoothing.loessv1_vs_loessv2
   python -m test.curve_smoothing.loess_vs_spline
   ```
3. (Optional) Open the Jupyter notebook to explore the algorithms:
   ```sh
   notebooks\curve_smoothing_algo.ipynb
   ```

---

## 🌍 GPX Track Processing and Elevation Analysis

Provides utilities for reading GPX files, retrieving elevation data, and comparing sources.

Distance between geographic coordinates is calculated using the Haversine formula, assuming the Earth's radius is 6371.0 km.

### Features

- Load GPX data using `Track.from_gpx_file()`
- Retrieve elevation data from online APIs via `track.with_api_elevations()`
- Smooth elevations using `track.with_smoothed_elevations()`
- Compare elevation profiles using:
  - `Plotter` for basic plotting
  - `SynchronizedElevationPlotter` for synchronized comparisons

---
## 📚 Documentation

- Class diagrams of core plotting classes are available in the [`docs/`](docs/) folder:

   1. [`class_diagram_elevation_api.md`](docs/class_diagram_elevation_api.md)
   2. [`class_diagram_models.md`](docs/class_diagram_models.md)
   3. [`class_diagram_plotter.md`](docs/class_diagram_plotter.md)

- Backend feature usage examples and notebooks:

   1. [`backend_feature_examples.ipynb`](docs/backend_feature_examples.ipynb)
   2.  [`curve_smoothing_algo.ipynb`](docs/curve_smoothing_algo.ipynb)

---

## 📄 License

This project is licensed under the MIT License.

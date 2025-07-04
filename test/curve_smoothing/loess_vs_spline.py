from src.curve_smoothing.loess_v2 import loess_v2
from src.curve_smoothing.loess_v1 import loess
from src.curve_smoothing.spline_fit import spline_fit
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    

    # Generate x values
    x = np.linspace(0, 10, 200)

    # True underlying function (e.g. smooth sine)
    y_true = np.sin(x) + 0.5 * np.sin(3 * x)

    # Add noise and spikes
    np.random.seed(0)
    noise = np.random.normal(0, 0.3, size=x.shape)
    spikes = (np.random.rand(len(x)) > 0.95) * np.random.normal(2, 1, size=x.shape)
    y_noisy = y_true + noise + spikes

    # Apply LOESS smoothing
    window = 0.2
    iters = 2
    s = 25
    k = 5
    smoothed_y = loess(x, y_noisy, window)
    smoothed_y2 = loess_v2(x, y_noisy, window, iters)
    smoothed_spline = spline_fit(x, y_noisy, s=s, k=k)

    # Plot the results
    plt.scatter(x, y_noisy, label='Noisy Data', alpha=0.5)
    plt.plot(x, y_true, color='green', label='Desired Curve')
    plt.plot(x, smoothed_y, color='blue', label=f'LOESS-v1 Smoothed (window:{window*100}%)')
    plt.plot(x, smoothed_y2, color='red', label=f'LOESS-v2 Smoothed (window:{window*100}%, iters:{iters})')
    plt.plot(x, smoothed_spline, color='yellow', label=f'Spline-fit Smoothed (S:{s}, K:{k})')
    plt.legend()
    plt.show()
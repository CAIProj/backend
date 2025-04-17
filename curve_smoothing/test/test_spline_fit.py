from src.spline_fit import spline_fit
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
    s = 25
    k = 5
    smoothed_y = spline_fit(x, y_noisy, s=s, k=k)

    # Plot the results
    plt.scatter(x, y_noisy, label='Noisy Data', alpha=0.5)
    plt.plot(x, y_true, color='green', label='Desired Curve')
    plt.plot(x, smoothed_y, color='red', label=f'Spline-fit Smoothed (S:{s}, K:{k})')
    plt.legend()
    plt.show()
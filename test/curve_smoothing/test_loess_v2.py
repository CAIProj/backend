from src.loess_v2 import loess_v2
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
    smoothed_y = loess_v2(x, y_noisy, window)

    # Plot the results
    plt.scatter(x, y_noisy, label='Noisy Data', alpha=0.5)
    plt.plot(x, y_true, color='green', label='Desired Curve')
    plt.plot(x, smoothed_y, color='red', label=f'LOESS-v2 Smoothed (window:{window*100}%)')
    plt.legend()
    plt.show()
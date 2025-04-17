"""
In this script, we will implement the LOESS (Locally Weighted Scatterplot Smoothing) algorithm.
Loess algorithm iteratively fits a polynomial regression model to the data points in a local neighborhood of each point.
The algorithm is particularly useful for smoothing scatterplots and can be used to fit non-linear relationships between variables.
local neighborhood is given as a fraction of the total number of points.

In this implemetation, we will use a 2nd degree polynomial model for the local polynomial fitting.
As per weights, we will use the tricube weight function. We only consider distances along the x-axis.
And the y-axis is CONSIDERED for the distance calculation.


input parameters:
    x: list of x values
    y: list of y values
    window: fraction of the total number of points to consider for the local neighborhood (default is 0.1)

output:
    smoothed_y: list of smoothed y values
"""

import numpy as np

def apply_weights(f_point, close_points):
    '''
    Apply weights to the current window of points.
    Formula: Tricube weighting function
    '''
    
    distances = np.abs(f_point - close_points)
    
    d = np.max(distances)
    if d == 0:
        return np.ones_like(distances)
    
    normalised = distances / d
    weights = (1 - normalised ** 3) ** 3
    weights[distances > 1] = 0
    return weights

def robust_weights(residuals):
    '''
    Apply robust weights to the residuals.
    Formula: Tukey's biweight function
    '''
    
    mad = np.median(np.abs(residuals - np.median(residuals)))
    if mad == 0:
        return np.ones_like(residuals).tolist()
    
    normalised = residuals /(6.0* mad)
    weights = (1 - normalised ** 2) ** 2
    weights[np.abs(normalised) >= 1] = 0
    return weights

def get_window(x, f_index, window_size):
    '''
    Get the closest neighbours of the current point.
    Distance is calculated as the absolute differnce between x values.
    '''
    distances = [(i,abs(xi - x[f_index])) for i, xi in enumerate(x)]

    closest_indeces = sorted(distances, key=lambda x: x[1])[:window_size]
    closest_indeces = [i for i, _ in closest_indeces]
    closest_indeces.sort()
    return [(i,x[i]) for i in closest_indeces]


def predict_point(f_point, x_window, y_window, window_size, weights):
    '''
    Fit a quadratic polynomial to the current window of points.
    return the predicted value for the current point by the polynomial.
    '''

    x = np.vstack([np.ones(window_size), x_window, x_window**2]).T

    #Apply weights
    w = np.diag(weights)

    #solve coefficients
    xtw = np.dot(x.T, w)
    xtwx = np.dot(xtw, x)
    xtwy = np.dot(xtw, y_window)

    #solve the system
    beta = np.linalg.solve(xtwx, xtwy)

    y_pred = beta[0] + beta[1] * f_point + beta[2] * f_point**2

    return y_pred


def loess_v2(x, y, window=0.1, iters=2):
    '''
    Apply LOESS smoothing to the data.
    return the smoothed y values.
    '''

    x = np.array(x)
    y = np.array(y)
    
    n = len(x)
    window_size = int(window * n)

    robust_w = np.ones(n)

    for _ in range(iters):
        smoothed_y = []

        # Iterarte over each point in x
        for i, xp in enumerate(x):

            # get the window
            x_window_data = get_window(x, i, window_size)
            y_window = np.array([y[i] for i, _ in x_window_data])
            x_window = np.array([xi for _, xi in x_window_data])
            index_window = [j for j, _ in x_window_data]

            x_weights = apply_weights(xp, x_window)
            combined_weights = np.array(x_weights) * robust_w[index_window]

            y_pred = predict_point(xp, x_window, y_window, window_size, combined_weights)
            smoothed_y.append(y_pred)

        smoothed_y = np.array(smoothed_y)

        if _ < iters - 1:
            residuals = y - smoothed_y
            robust_w = robust_weights(residuals)

    return smoothed_y
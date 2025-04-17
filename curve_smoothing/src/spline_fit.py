'''
In this script, we will fit a spline to the given data pointsusing the scipy.
interpolate.UnivariateSpline class.

Input:
    x: x-coordinates of the data points
    y: y-coordinates of the data points
    s: smoothing factor (float) - the larger the value, the smoother the spline
    k: degree of the spline (int) - default is 3, which is cubic spline

return:
    smoothed_y: y-coordinates of the spline
'''

import scipy
from scipy.interpolate import UnivariateSpline
import numpy as np

def spline_fit(x: list, y: list, s: float = 25, k: int = 3) -> list:

    x = np.array(x)
    y = np.array(y)

    spline = UnivariateSpline(x, y, s=s, k=k)  # s=0 means interpolation
    y_pred = spline(x)

    return y_pred.tolist()

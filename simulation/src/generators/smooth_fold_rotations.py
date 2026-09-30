import numpy as np

def Q_1(theta):
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    return np.matrix([1, 0, 0, 0],
                     [0, cos, -sin, 0],
                     [0, sin, cos, 0],
                     [0, 0, 0, 1])
    
def Q_3(theta):
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    return np.matrix([cos, -sin, 0, 0],
                     [sin, cos, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1])
    
def T(b):
    """
        b is a 3 elem vector
    """
    
    return np.matrix([1, 0, 0, b[0]],
                     [0, 1, 0, b[1]],
                     [0, 0, 1, b[2]],
                     [0, 0, 0, 1])
    
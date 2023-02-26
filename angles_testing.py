import numpy as np

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def finger_angles(vects):
    total_curl = 0
    for i in range(len(vects)-1):
        total_curl += angle_between(vects[i], vects[i+1])
    return total_curl

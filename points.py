import numpy as np

# Class to hold a point
class point():
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

# get distance between 2 points
def distance_between(a,b):
    a = np.array([a.x,a.y,a.z])
    b = np.array([b.x,b.y,b.z])
    dist = a-b

    return np.sqrt(sum(dist*dist))

def get_velocity(a,b):
    return point(a.x-b.x, a.y-b.y, a.z-b.z)

def get_hand_vel(pos):
    hand = pos[-1]
    if len(pos) > 1:
        hand_old = pos[-2]
    else:
        hand_old = pos[-1]

    vels = []
    for i in range(len(hand)):
        vels.append(get_velocity(hand[i], hand_old[i]))

    return vels

def get_ratio_point(pos, ratio):
    return point(pos.x, pos.y*ratio, pos.z)
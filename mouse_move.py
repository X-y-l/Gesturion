import mouse
import numpy as np
import pyautogui as pagui
width, height = pagui.size()

def move_mouse(old_pos_hand, new_pos_hand):

    old_pos_mouse = [old_pos_hand.x * width, old_pos_hand.y*height]
    new_pos_mouse = [new_pos_hand.x * width, new_pos_hand.y*height]

    move_vect = np.array([old_pos_mouse[0] - new_pos_mouse[0], old_pos_mouse[1] - new_pos_mouse[1]])
    move_vect = np.sign(move_vect) * np.power(move_vect,2)

    move_vect = move_vect * 0.02
    #print(move_vect)

    mouse.move(move_vect[0], -move_vect[1], False)
    #mouse.drag(0,0, move_vect[0], -move_vect[1], False, duration=0.016)

#move_mouse([0,0],[10,-10])
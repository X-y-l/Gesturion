import mouse
import numpy as np
import pyautogui as pagui

width, height = pagui.size()

def move_mouse(old_pos_hand, new_pos_hand):

    old_pos_mouse = [old_pos_hand.x * width, old_pos_hand.y*height]
    new_pos_mouse = [new_pos_hand.x * width, new_pos_hand.y*height]

    move_vect = [new_pos_mouse[0] - old_pos_mouse[0], new_pos_mouse[1] - old_pos_mouse[1]]
    mouse.move(move_vect[0], -move_vect[1], False)
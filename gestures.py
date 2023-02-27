from mouse_move import move_mouse
from points import point, distance_between, get_ratio_point
import mouse
import pyautogui as pagui
import numpy as np
import keyboard
import time

def nothing():
    pass

class Gestures:
    def __init__(self):
        self.calls = [
            [self.speaking_check, self.speaking_toggle, nothing, self.speaking_toggle],
            [self.scroll_check, self.scroll, self.scroll, nothing],
            [self.point_check, self.point, self.point, nothing],
            [lambda: True, nothing, nothing, nothing]
            ]
        self.click_len = 5
        self.left = [False]*self.click_len
        self.left_click = False
        self.right = [False]*self.click_len
        self.right_click = False
        self.hist_len = 20
        self.hist = [None]*self.hist_len
        self.last = None

    def pass_data(self, hand_pos, hand_vel, finger_curl, finger_up, conv_factor, face):
        self.hand_pos = hand_pos
        self.hand_vel = hand_vel
        self.finger_curl = finger_curl
        self.finger_up = finger_up
        self.conv_factor = conv_factor
        self.face = face

    def run_all(self):
        current = None
        for i, c in enumerate(self.calls):
            if c[0]():
                current = i
                break
        self.hist.append(current)
        self.hist = self.hist[1:]

        if self.last is not None:
            self.calls[self.last][2]()

        best = 0
        best_action = None
        for i in range(len(self.calls)):
            amount = 0
            for j in self.hist:
                if j == i:
                    amount += 1
            if amount > best:
                best = amount
                best_action = j

        if best_action != self.last:
            if self.last is not None:
                self.calls[self.last][3]()
            if best_action is not None:
                self.last = best_action
                self.calls[best_action][1]()
            


    # Speaking
    def speaking_toggle(self):
        keyboard.send("win+h")
    
    def speaking_check(self):
        f_up = self.finger_up[-1]
        return self.face[-1] and f_up[1:] == [1,0,0,0]

    # Pointing
    def point_check(self):
        f_up = self.finger_up[-1]
        return f_up[3] == 0 and f_up[4] == 0 and f_up[0] == 1
        
    def point(self):
        old_finger = self.hand_pos[-1][5]
        touch_point = self.hand_pos[-2][5]

        self.left.append(self.l_click_check())
        self.right.append(self.r_click_check())

        self.left = self.left[1:]
        print(self.left)
        self.right = self.right[1:]

        if sum(self.left) > 3 and not self.left_click:
            self.l_click_start()
            print("click")
            self.left_click = True
        if sum(self.left) < 1 and self.left_click:
            self.l_click_stop()
            self.left_click = False

        if sum(self.right) > 3 and not self.right_click:
            self.r_click_start()
            print("unclick")
            self.right_click = True
        if sum(self.right) < 1 and self.right_click:
            self.r_click_stop()
            self.right_click = False


        move_mouse(touch_point,old_finger,self.conv_factor)

    # scrolling
    def scroll_check(self):
        f_up = self.finger_up[-1]
        return f_up[1:] == [0,0,0,0]

    def scroll(self):
        scroll_dist = 0.2*self.conv_factor
        clicks = self.hand_vel[-1][4].y//scroll_dist
        print(clicks)
        mouse.wheel(clicks)

    # Click
    def l_click_check(self):
        hand = self.hand_pos[-1]
        dist = 5
        if distance_between(hand[4], hand[8]) < dist*self.conv_factor:
            return True
        return False
    
    def l_click_start(self):
        mouse.press()

    def l_click_stop(self):
        mouse.release()

    def r_click_check(self):
        hand = self.hand_pos[-1]
        dist = 2
        if distance_between(hand[4], hand[12]) < dist*self.conv_factor:
            return True
        return False

    def r_click_start(self):
        mouse.press("right")
    
    def r_click_stop(self):
        mouse.release("right")

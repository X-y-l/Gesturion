from mouse_move import move_mouse
from points import point, distance_between, get_ratio_point
import mouse
import keyboard

class Gestures:
    def __init__(self):
        self.scroll_speed = 0
        self.recording = False

    def pass_data(self, hand_pos, hand_vel, finger_curl, finger_up, conv_factor, face):
        self.hand_pos = hand_pos
        self.hand_vel = hand_vel
        self.finger_curl = finger_curl
        self.finger_up = finger_up
        self.conv_factor = conv_factor
        self.face = face

    def run_all(self):
        if self.recording:
            self.speaking()
            #mouse.release()
        else:
            if not self.scroll():
                if not self.point():
                    self.speaking()
                self.click()

    def speaking(self):
        f_up = self.finger_up[-1]
        if self.face[-1] and not self.face[-2] and f_up[1:] == [1,0,0,0]:
            keyboard.send("win+h")
            self.recording = False
        if self.face[-2] and not self.face[-1] and self.recording:
            keyboard.send("win+h")
            self.recording = True
        if self.face[-1] and f_up[1:] == [1,0,0,0]:
            return True
        return False

    def point(self):
        f_up = self.finger_up[-1]
        if f_up[3] == 0 and f_up[4] == 0 and f_up[0] == 1:
            old_finger = self.hand_pos[-1][5]
            touch_point = self.hand_pos[-2][5]
            move_mouse(touch_point,old_finger)
            return True
        
        return False

    def scroll(self):
        f_up = self.finger_up[-1]
        scroll_dist = 0.2*self.conv_factor
        if f_up[1:] == [0,0,0,0]:
            clicks = self.hand_vel[-1][4].y//scroll_dist
            print(clicks)
            mouse.wheel(clicks)
            if clicks != 0:
                return True
        else:
            return False


    def click(self):
        hand = self.hand_pos[-1]
        dist = 5
        dist_r = 2
        old_hand = self.hand_pos[-2]
        clicked = False
        if distance_between(old_hand[4], old_hand[8]) > dist*self.conv_factor:
            if distance_between(hand[4], hand[8]) < dist*self.conv_factor:
                mouse.press()
                clicked = True
        if distance_between(old_hand[4], old_hand[8]) < dist*self.conv_factor:
            if distance_between(hand[4], hand[8]) > dist*self.conv_factor:
                mouse.release()

        if distance_between(old_hand[4], old_hand[12]) > dist_r*self.conv_factor:
            if distance_between(hand[4], hand[12]) < dist_r*self.conv_factor:
                mouse.press(button="right")
                clicked = True
        if distance_between(old_hand[4], old_hand[12]) < dist_r*self.conv_factor:
            if distance_between(hand[4], hand[12]) > dist_r*self.conv_factor:
                mouse.release(button="right")
        return clicked

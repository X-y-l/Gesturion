import cv2

# Define the font properties
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (0, 55, 255)
line_type = cv2.LINE_AA

def draw_text(image, text, pos):
    cv2.putText(image, text, pos, font, font_scale, font_color, thickness=2, lineType=line_type)
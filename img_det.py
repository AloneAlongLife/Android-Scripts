import cv2
import numpy as np

DEBUG = False

def int_retouch(min_val: int, max_val: int, val: int) -> int:
    return int(max(min_val, min(max_val, val)))

def find(template: cv2.Mat, src: cv2.Mat, threshold=0.05, debug=False) -> tuple[bool, tuple[int, int]]:
    hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV).copy()
    unique, counts = np.unique(hsv_template.reshape(-1, 3), axis=0, return_counts=True)
    h, s, v = unique[np.argmax(counts)]

    lower_val = (
        int_retouch(0, 180, h - 5),
        int_retouch(0, 255, s - 5),
        int_retouch(0, 255, v - 5),
    )
    upper_val = (
        int_retouch(0, 180, h + 5),
        int_retouch(0, 255, s + 5),
        int_retouch(0, 255, v + 5),
    )

    template_mask = cv2.inRange(hsv_template, lower_val, upper_val)
    template[template_mask == 0] = 0

    src_mask = cv2.inRange(cv2.cvtColor(src, cv2.COLOR_BGR2HSV), lower_val, upper_val)
    src[src_mask == 0] = 0

    min_val, max_val, min_pos, _ = cv2.minMaxLoc(cv2.matchTemplate(src, template, cv2.TM_SQDIFF_NORMED))

    t_h, t_w, _ = template.shape
    center_x = min_pos[0] + t_w // 2
    center_y = min_pos[1] + t_h // 2
    res = min_val < threshold
    pos = (center_x, center_y)

    if DEBUG or debug:
        print(min_val, max_val, res, pos)
        src = cv2.rectangle(src, min_pos, (min_pos[0]+t_w, min_pos[1]+t_h), (0, 0, 255), 2, )
        cv2.imwrite("debug.png", src)
        input("WAIT")

    return res, pos
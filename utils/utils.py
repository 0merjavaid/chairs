import os
import cv2
import urllib
import numpy as np


def parse_cfg(path):
    mapping = dict()
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:
            bottom_rights = list()
            line = line.split(",")
            line[1] = int(line[1])
            line[2] = int(line[2])
            line[4] = float(line[4])
            tuples = line[3].split(" ")
            for i in range(0, len(tuples), 2):
                bottom_rights.append([int(tuples[i]), int(tuples[i+1])])
            line[3] = bottom_rights
            mapping[line[0]] = line[1:]
    return mapping


def download_img(store_path, url, index):
    store_path = os.path.join(store_path, str(index)+".jpg")
    urllib.request.urlretrieve(url, store_path)
    return store_path


def resize_conversion(chair, bg_height, max_height, chair_height):
    orig_h, orig_w, _ = chair.shape
    scaling_factor = float(chair_height) / max_height
    new_h = int(bg_height*scaling_factor)
    width_scaling_factor = float(orig_h)/new_h
    new_w = int(orig_w/width_scaling_factor)
    return new_h, new_w


def get_mask(image):
    divisor = 1.5
    image[(image[:, :, 0] > 240)*(image[:, :, 1] > 240)
          * (image[:, :, 2] > 240)] = 0
    mask = np.zeros_like(image)
    mask[image != 0] = 1
    mask[:int(mask.shape[0]/divisor), :, 1] = cv2.erode(mask[:int(mask.shape[0]/divisor), :, 1],
                                                        np.ones((3, 3)), iterations=1)
    mask[:int(mask.shape[0]/divisor), :, 1] = cv2.morphologyEx(mask[:int(mask.shape[0]/divisor), :, 1],
                                                               cv2.MORPH_CLOSE, np.ones((3, 3)), iterations=6)

    mask[int(mask.shape[0]/divisor):, :, 1] = cv2.erode(mask[int(mask.shape[0]/divisor):, :, 1],
                                                        np.ones((3, 3)), iterations=3)
    mask[int(mask.shape[0]/divisor):, :, 1] = cv2.morphologyEx(mask[int(mask.shape[0]/divisor):, :, 1],
                                                               cv2.MORPH_CLOSE, np.ones((3, 3)), iterations=3)
    mask = cv2.cvtColor(mask[:, :, 1], cv2.COLOR_GRAY2RGB)
    image = image*mask
    return mask


def get_shadow(img, shadow_x, shadow_y, intensity, spread_x):
    shadow = np.zeros_like(img).astype(float)
    shadow = shadow[:, :, 0]
    scaling_factor = 4
    shadow = cv2.resize(shadow, (int(
        shadow.shape[1]/scaling_factor), int(shadow.shape[0]/scaling_factor)))

    cv2.ellipse(shadow, (int(shadow_x/scaling_factor), int(shadow_y/scaling_factor)),
                (int(spread_x/(scaling_factor*1.5)), int(spread_x/(scaling_factor*10))), 0, 0, 360, 1, -1)
    shadow = cv2.GaussianBlur(shadow, (129, 129), 0)

    shadow *= intensity
    shadow = cv2.resize(shadow, (img.shape[1], img.shape[0]))
    shadow = 1-shadow
    # cv2.imshow("shadow", shadow)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return np.stack((shadow,)*3, axis=-1)

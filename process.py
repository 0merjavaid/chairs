import cv2
import glob
import numpy as np
from utils.utils import *
from data.csv_parser import *


def main():
    bgs = glob.glob("data/backgrounds/*jpg")
    master = Master("data/itembuilder.csv")
    for room_cnt, background_path in enumerate(bgs):
        background_mapping = parse_cfg("config/chairs.conf")
        del_bottom, bg_height, bottom_rights, shadow_intensity = background_mapping[
            background_path.split("/")[-1].split(".")[0]]

        max_height = 48
        i = 0
        while True:
            try:
                sku, chair_height, download_path = next(master.get_item())
            except Exception as e:
                break
            i += 1

            print("Creating Image: ", i, "/",
                  master.total_items, " For room: ", room_cnt+1, "/ 5")
            chair_path = download_img(
                "temp/", download_path, 1)

            room = cv2.imread(background_path)
            if chair_path == "":
                print (chair_path, "Doesnt exists")
                continue
            chair = cv2.imread(chair_path)
            os.remove(chair_path)
            try:
                h, w = chair.shape[:2]
            except Exception as e:
                print ("Skipping", sku)
                continue
            resized_h, resized_w = resize_conversion(
                chair, bg_height, max_height, chair_height)

            mask = get_mask(chair.copy())

            mask, chair = cv2.resize(
                mask, (resized_w, resized_h)), cv2.resize(chair, (resized_w, resized_h))
            mask = mask[:-del_bottom]
            chair = chair[:-del_bottom]
            new_h, new_w = chair.shape[:2]
            for cnt, bottom_right in enumerate(bottom_rights):
                if cnt % 2 != 0:
                    chair = np.fliplr(chair)
                    mask = np.fliplr(mask)
                if bottom_right[0] >= room.shape[0]:
                    bottom_right[0] = room.shape[0]-1
                y_start = bottom_right[0]-new_h
                x_start = bottom_right[1]-new_w

                room = room * \
                    get_shadow(
                        room, shadow_x=int((bottom_right[1]+x_start)/2),
                        shadow_y=int(bottom_right[0]-(bottom_right[0]*0.05)), intensity=shadow_intensity, spread_x=new_w)
                room[y_start:bottom_right[0],
                     x_start:bottom_right[1]] *= (1-mask)
                room[y_start:bottom_right[0],
                     x_start:bottom_right[1]] += chair*mask

            save_path = "data/outputs/"+background_path.split(
                "/")[-1].split(".")[0] + download_path.split("/")[-1]
            cv2.imwrite(save_path, room.astype("uint8"))
        # show_image((room).astype("uint8"))
        # cv

main()

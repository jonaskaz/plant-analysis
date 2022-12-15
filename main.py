import os
from dotenv import load_dotenv
from datetime import datetime
from plantcv import plantcv as pcv
import matplotlib
import numpy as np
import traceback
from datetime import date, timedelta
import sys

sys.path.append("./notebooks")
from image_helper import ImageHelper

load_dotenv()

base_url = os.environ.get("STORAGE_URL")
assert base_url
im_helper = ImageHelper(base_url)


# Set debug to the global parameter
pcv.params.debug = None


def load_images(dt):
    assert im_helper.get(dt, "side")
    side_img, path, filename = pcv.readimage(im_helper.image.name)
    side_crop_img = pcv.crop(img=side_img, x=300, y=470, h=1100, w=2800)
    assert im_helper.get(dt, "top")
    top_img, path, filename = pcv.readimage(im_helper.image.name)
    top_crop_img = pcv.crop(img=top_img, x=730, y=480, h=1430, w=1980)
    return side_crop_img, top_crop_img


def filter_top_image(crop_img):
    corrected_img = pcv.white_balance(img=crop_img, mode="hist", roi=[280, 120, 5, 5])
    rotate_img = pcv.transform.rotate(corrected_img, 2, True)
    gray_img = pcv.rgb2gray_lab(rgb_img=rotate_img, channel="b")
    return gray_img


def filter_side_image(crop_img):
    rotate_img = pcv.transform.rotate(crop_img, -1, True)
    gray_img = pcv.rgb2gray_lab(rgb_img=rotate_img, channel="l")
    return gray_img


def create_top_mask(gray_img):
    thresh = pcv.threshold.binary(
        gray_img=gray_img, threshold=55, max_value=255, object_type="dark"
    )
    rois, roi_hierarchy = pcv.roi.multi(
        img=gray_img, coord=(550, 460), radius=180, spacing=(550, 580), nrows=2, ncols=3
    )
    roi_mask = pcv.roi.roi2mask(img=gray_img, contour=rois[0])
    for r in rois:
        new_mask = pcv.roi.roi2mask(img=gray_img, contour=r)
        roi_mask = np.maximum(roi_mask, new_mask)
    combined_mask = np.minimum(roi_mask, thresh)
    filled_mask = pcv.fill(bin_img=combined_mask, size=200)
    # pcv.plot_image(filled_mask)
    return filled_mask, rois, roi_hierarchy


def create_side_mask(gray_img):
    thresh = pcv.threshold.binary(
        gray_img=gray_img, threshold=80, max_value=255, object_type="light"
    )
    rect_contour1, rect_hierarchy1 = pcv.roi.rectangle(
        img=gray_img, x=400, y=300, h=800, w=550
    )
    rect_contour2, rect_hierarchy2 = pcv.roi.rectangle(
        img=gray_img, x=1000, y=300, h=800, w=550
    )
    rect_contour3, rect_hierarchy3 = pcv.roi.rectangle(
        img=gray_img, x=1850, y=400, h=700, w=550
    )
    rois = [rect_contour1, rect_contour2, rect_contour3]
    roi_hierarchy = [rect_hierarchy1, rect_hierarchy2, rect_hierarchy3]
    roi_mask = pcv.roi.roi2mask(img=gray_img, contour=rois[0])
    for r in rois:
        new_mask = pcv.roi.roi2mask(img=gray_img, contour=r)
        roi_mask = np.maximum(roi_mask, new_mask)
    combined_mask = np.minimum(roi_mask, thresh)
    filled_mask = pcv.fill_holes(bin_img=combined_mask)
    filled_mask = pcv.fill(bin_img=combined_mask, size=200)
    # pcv.plot_image(filled_mask)
    return filled_mask, rois, roi_hierarchy


def analyze_shape(rois, roi_hierarchy, crop_img, mask):
    obj, obj_hierarchy = pcv.find_objects(img=crop_img, mask=mask)
    plant_ids = range(0, len(rois))
    img_copy = np.copy(crop_img)
    pixel_heights = []
    pixel_areas = []
    # Create a for loop to interate through every ROI (plant) in the image
    for i in range(0, len(rois)):
        roi = rois[i]
        hierarchy = roi_hierarchy[i]
        plant_id = plant_ids[i]
        # Subset objects that overlap the ROI
        plant_contours, plant_hierarchy, mask, area = pcv.roi_objects(
            img=crop_img,
            roi_contour=roi,
            roi_hierarchy=hierarchy,
            object_contour=obj,
            obj_hierarchy=obj_hierarchy,
            roi_type="partial",
        )

        # If the plant area is zero then no plant was detected for the ROI
        # and no measurements can be done
        if area > 0:
            # Combine contours together for each plant
            plant_obj, plant_mask = pcv.object_composition(
                img=crop_img, contours=plant_contours, hierarchy=plant_hierarchy
            )
            # Analyze the shape of each plant
            img_copy = pcv.analyze_object(
                img=img_copy, obj=plant_obj, mask=plant_mask, label=f"plant{plant_id}"
            )
            pixel_heights.append(
                pcv.outputs.observations[f"plant{plant_ids[i]}"]["height"]["value"]
            )
            pixel_areas.append(
                pcv.outputs.observations[f"plant{plant_ids[i]}"]["area"]["value"]
            )
    return pixel_heights, pixel_areas, img_copy


def expand_pixel_heights(pixel_heights):
    """
    Pretend pixel heights are captured for all plants
    """
    pixel_heights_adjusted = []
    for p in pixel_heights:
        pixel_heights_adjusted.append(p)
        pixel_heights_adjusted.append(p)
    return pixel_heights_adjusted


def reorder_areas_to_match_heights(pixel_areas):
    areas = []
    areas.append(pixel_areas[0])
    areas.append(pixel_areas[3])
    areas.append(pixel_areas[1])
    areas.append(pixel_areas[4])
    areas.append(pixel_areas[2])
    areas.append(pixel_areas[5])
    return areas


def calculate_plant_size(pixel_heights, pixel_areas):
    """
    Calculate the real world size of the plants
    """
    # constants
    hor_dist_front_plant = 125  # mm
    hor_dist_back_plant = 165  # mm
    dist_to_soil = 200  # mm
    K = np.matrix(
        [
            [2719, 0.000000, 3280 / 2],
            [0.000000, 2719, 2464 / 2],
            [0.000000, 0.000000, 1.000000],
        ]
    )

    plant_height = []
    plant_area = []

    for i in range(0, len(pixel_heights)):

        # calculate plant height
        if i % 2 == 0:
            plant_height.append(hor_dist_back_plant / 2719 * pixel_heights[i])
        else:
            plant_height.append(hor_dist_front_plant / 2719 * pixel_heights[i])

        # calculate plant area
        vert_dist_to_plant = dist_to_soil - plant_height[i]
        plant_area.append(vert_dist_to_plant**2 / 2719**2 * pixel_areas[i])

    return plant_height, plant_area


def process_images(dt):
    try:
        side_image, top_image = load_images(dt)
        pcv.print_image(
            side_image, "side/cropped/" + str(dt).replace("/", "-") + ".jpeg"
        )
        pcv.print_image(top_image, "top/cropped/" + str(dt).replace("/", "-") + ".jpeg")
        side_gray_img = filter_side_image(side_image)
        top_gray_img = filter_top_image(top_image)
        side_mask, side_rois, side_roi_hierarchy = create_side_mask(side_gray_img)
        pcv.print_image(side_mask, "side/mask/" + str(dt).replace("/", "-") + ".jpeg")
        top_mask, top_rois, top_roi_hierarchy = create_top_mask(top_gray_img)
        pcv.print_image(top_mask, "top/mask/" + str(dt).replace("/", "-") + ".jpeg")
        pixel_heights, _, img_copy = analyze_shape(
            side_rois, side_roi_hierarchy, side_image, side_mask
        )
        pcv.print_image(img_copy, "side/plants/" + str(dt).replace("/", "-") + ".jpeg")
        print(f"Found {len(pixel_heights)} plants from side")
        pixel_heights = expand_pixel_heights(pixel_heights)
        _, pixel_areas, img_copy = analyze_shape(
            top_rois, top_roi_hierarchy, top_image, top_mask
        )
        pcv.print_image(img_copy, "top/plants/" + str(dt).replace("/", "-") + ".jpeg")
        print(f"Found {len(pixel_areas)} plants from top")
        pixel_areas = reorder_areas_to_match_heights(pixel_areas)
        plant_heights, plant_areas = calculate_plant_size(pixel_heights, pixel_areas)
        return plant_heights, plant_areas
    except Exception:
        print(traceback.format_exc())
        print(f"Skipping, could not process images for {dt}")
        return [], []


def datetimerange(start_dt, end_dt):
    delta = end_dt - start_dt
    hours_delta = delta.days * 24 + delta.seconds / 60 / 60
    for n in range(int(hours_delta)):
        yield start_dt + timedelta(hours=n)


if __name__ == "__main__":
    import json

    # end '14/12/2022 4:08:18'
    results_filepath = "results.json"
    start_dt = im_helper.dt_from_string("13/12/2022 0:08:18")
    end_dt = im_helper.dt_from_string("13/12/2022 0:08:18")
    plant_heights = {}
    plant_areas = {}
    for dt in datetimerange(start_dt, end_dt):
        height, area = process_images(dt)
        if len(height) == 0:
            continue
        print(dt)
        print(height)
        print(area)
        with open(results_filepath) as f:
            data = json.load(f)

        data["height"][str(dt)] = height
        data["area"][str(dt)] = area

        with open(results_filepath, "w") as f:
            json.dump(data, f)

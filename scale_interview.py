### Checks 
# Are labels and attribute values valid?
# Are bounding boxes values valid?


import scaleapi
import json 
import csv
import cv2
import numpy as np
import urllib.request
from PIL import Image
#from sklearn.cluster import KMeans
from collections import Counter

OUTPUT_FILE_PATH = 'result.csv'

COLOR_DICT = {"white": {255, 255, 255},
              "red" : {255, 0, 0},
              "orange" : {255, 150, 0},
              "yellow": {255, 235, 0},
              "green": {0, 200, 0},
              "blue": {67, 133, 255},
              "grey": {128, 128, 128}
}


def url_to_image(image_url):
    with urllib.request.urlopen(image_url) as url:
        image = np.asarray(bytearray(url.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image

def check_status_completed(task_status):
    return task_status == "completed"

def check_boundingbox_area(task_id, annotation_uuid, task_image_area, annotation_width, annotation_height):  ### Maximum and Minimum area bounds - Work with IoU to find what percentage of the picture does the bounding box cover
    bounding_box_area = annotation_width * annotation_height
    bounding_box_percentage = bounding_box_area/task_image_area

    status, description = "" , ""
    if bounding_box_percentage > 0.5:
        status = "ERROR"
        decription = "Bounding box is too big to be correct."
    elif bounding_box_percentage > 0.25:
        status = "WARN"
        description = "Bounding box may be big to be correct."

    return status, description

def check_background_color(task_id, annotation_uuid, task_image, annotation_width, annotation_height, annotation_top, annotation_left, annotation_bgcolor, annotation_label): # Find dominant color within the bounding box and see if its identical to the label attribute
    # Find dominant color inside bounding box (You can use KMeans or try finding the most commonly ocurring color)
    print(task_id, annotation_uuid)
    
    image = task_image[annotation_top: annotation_top + annotation_height][annotation_left:annotation_left + annotation_width][:]
    w, h = image.size
    pixels = image.getcolors(w*h)

    most_frequent_pixel = pixels[0]

    for count, color in pixels:
        if count > most_frequent_pixels[0]:
            most_frequent_pixel = (count, color)
    
    ## Find the closest label for the dominant color from COLOR_DICT (Use Euclidean distance)

    ## Check if annotation_bgcolor is equal to dominant color label (for color BLUE, RED, YELLOW, ORANGE AND GREEN)
    ## For non_visible_face labels, label color should be grey
    ## Check if construction_sign is orange

    status, description = "" , ""
    return status, description


def box_inside_box(): # Overlapping box check
    pass

def check_bottom(): # Check for traffic signs - they shoud be located on top and on left/right (Assuming all pictures are taken from cars)
    pass

def aspect_ratio(): # Check for traffic lights - Color should be 'other'
    pass

client = scaleapi.ScaleClient('live_74275b9b2b8b44d8ad156db03d2008ed')

tasks = client.tasks(project="Traffic Sign Detection")

with open(OUTPUT_FILE_PATH, 'w') as csvfile:
    csv_fieldnames = ['task_id', 'task_completed', 'bounding_box_uuid', 'status', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
    writer.writeheader()

    for task in tasks:

        task_id = task.param_dict['task_id']
        task_status = task.param_dict['status']

        task_instruction = task.param_dict['instruction']
        
        task_image_url = task.param_dict['params']['attachment']
        task_image = url_to_image(task_image_url)
        task_image_width = task_image.shape[0]
        task_image_height = task_image.shape[1]
        task_image_area = task_image_width * task_image_height

        task_annotations = task.param_dict['response']['annotations']

        completed = check_status_completed(task_status)
        if not completed:
            writer.writerow({'task_id': task_id, 'completed': 'No'})
            continue
        
        for annotation in task_annotations:
            annotation_label = annotation['label']
            annotation_occlusion = annotation['attributes']['occlusion']
            annotation_truncation = annotation['attributes']['truncation']
            annotation_bgcolor = annotation['attributes']['background_color']
            annotation_width = annotation['width']
            annotation_height = annotation['height']
            annotation_uuid = annotation['uuid']
            annotation_left = annotation['left']
            annotation_top = annotation['top']

            status, description = check_boundingbox_area(task_id, annotation_uuid, task_image_area, annotation_width, annotation_height)
            if status and description:
                writer.writerow({'task_id': task_id, 'bounding_box_uuid': annotation_uuid, 'status': status, 'description': description})
            
            
            status, description = check_background_color(task_id, annotation_uuid, task_image, annotation_width, annotation_height, int(annotation_top), int(annotation_left), annotation_bgcolor, annotation_label)
            if status and description:
                writer.writerow({'task_id': task_id, 'bounding_box_uuid': annotation_uuid, 'status': status, 'description': description})
            
        
    



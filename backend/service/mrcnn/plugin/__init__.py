''' plugin '''
import ctypes.util
import imp
import json
import logging
from distutils.version import LooseVersion
import os

import cv2
import numpy as np
import skimage
import tensorflow.keras as keras

PLUGIN_DIR = os.path.dirname(__file__)

class Plugin():
  ''' plugin '''

  def __init__(self, mode: str, name: str, option):
    file, filename, desc = imp.find_module(name, path=[PLUGIN_DIR])
    self.mode = mode
    self.module = imp.load_module(name, file, filename, desc)

    # After python 3.8, add_dll_directory should be invoke before loading cuda lib
    if LooseVersion(keras.__version__) >= LooseVersion('2.7.0'):
      dll_path = ctypes.util.find_library("cudnn_cnn_infer64_8")
      if dll_path is None:
        logging.warning("cannot find cuda_bin_path!")
      else:
        cuda_bin_path = os.path.dirname(dll_path) + os.path.sep
        logging.info("cuda_bin_path: %s", cuda_bin_path)
        os.add_dll_directory(cuda_bin_path)
        from ctypes import WinDLL
        cudnn_cnn_infer64_8 = WinDLL("cudnn_cnn_infer64_8.dll")
        cudnn_cnn_infer64_8 = WinDLL("cudnn_ops_train64_8.dll")

    # Directory to save logs and trained model
    self.model_dir = option.model_path

    self.module.init(self)

  def detect(self, dataset_path, image_name):
    ''' detect '''
    image_path = os.path.join(dataset_path, "source", image_name)
    image = skimage.io.imread(image_path)
    # image = cv2.imread(image_path)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    r = self.model.detect([image], verbose=1)[0]
    return save_annotation(
      dataset_path, image_name, image.shape,
      self.module.get_class_names(self), 
      r["rois"], r["class_ids"], r["masks"], r["scores"]
    )

  def release():
    ''' release '''
    keras.backend.clear_session()

  def train(self, dataset_dir):
    ''' train '''
    self.module.train(self, dataset_dir)

def save_annotation(
  dataset_path, image_name, image_shape, 
  class_names, boxes, class_ids, masks, scores,
  save_polygon=False
  ):
  """
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    class_ids: [num_instances]
    masks: [height, width, num_instances]
    scores: (optional) confidence scores for each box
  """
  annotation_dir = os.path.join(dataset_path, "annotation", image_name)
  os.makedirs(annotation_dir, exist_ok=True)

  instance_count = boxes.shape[0]
  height, width = image_shape[:2]

  instances = []
  for i in range(instance_count):
    if not np.any(boxes[i]):
      # Skip this instance. Has no bbox. Likely lost in image cropping.
      continue

    mask = masks[:, :, i]
    mask_file_name = "mask_%d.png" % (i)
    mask_file_path = os.path.join(annotation_dir, mask_file_name)
    save_mask(mask_file_path, height, width, mask)

    polygon = []
    if save_polygon:
      # Pad to ensure proper polygons for masks that touch image edges.
      padded_mask = np.zeros(
          (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
      padded_mask[1:-1, 1:-1] = mask
      for verts in skimage.measure.find_contours(padded_mask, 0.5):
        # Subtract the padding and flip (y, x) to (x, y)
        verts = np.fliplr(verts) - 1
        polygon.append(verts.tolist())

    class_id = int(class_ids[i])
    
    b_box = boxes[i].tolist()
    instances.append({
      # [left, top, right, bottom]
      "roi": [b_box[1], b_box[0], b_box[3], b_box[2]],
      "mask": mask_file_name,
      "polygon": polygon,
      "class": class_names[class_id],
      "scores": float(scores[i]),
    })

  annotation = {
    "instances": instances
  }
  annotation_path = os.path.join(annotation_dir, "annotation.json")
  with open(annotation_path, 'w') as fp:
    json.dump(annotation, fp)
  return annotation_path

def save_mask(file_path, height, width, mask):
  image = np.ones([height, width, 3], dtype=np.uint8)
  color = [255, 255, 255] # BGR
  for c in range(3):
    image[:, :, c] = np.where(
      mask == 1,
      color[c],
      image[:, :, c]
    )
  cv2.imwrite(file_path, image)

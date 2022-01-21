''' coco plugin '''
import logging
import os

from . import config
from .dataset import CocoDataset
from backend.service.mrcnn import (model as modellib)

# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = [
  'BG', 'person', 'bicycle', 'car', 'motorcycle',
  'airplane', 'bus', 'train', 'truck', 'boat',
  'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
  'bird', 'cat', 'dog', 'horse', 'sheep',
  'cow', 'elephant', 'bear', 'zebra', 'giraffe',
  'backpack', 'umbrella', 'handbag', 'tie', 'suitcase',
  'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
  'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
  'bottle', 'wine glass', 'cup', 'fork', 'knife',
  'spoon', 'bowl', 'banana', 'apple', 'sandwich',
  'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
  'donut', 'cake', 'chair', 'couch', 'potted plant',
  'bed', 'dining table', 'toilet', 'tv', 'laptop',
  'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
  'oven', 'toaster', 'sink', 'refrigerator', 'book',
  'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
  'toothbrush'
]

def get_class_names(self):
  return class_names

def init(self) -> None:
  if self.mode == "inference":
    conf = config.InferenceConfig()
  elif self.mode == "training":
    conf = config.TrainConfig()
  
  self.model = modellib.MaskRCNN(mode=self.mode, model_dir=self.model_dir, config=conf)

  # Load weights trained
  model_path = os.path.join(self.model_dir, "mask_rcnn_coco.h5")
  # model_path = self.model.get_imagenet_weights(self.model_dir)
  self.model.load_weights(model_path, by_name=True)

def train(self, dataset_dir, year = "2014"):
  # Training dataset. Use the training set and 35K from the
  # validation set, as as in the Mask RCNN paper.
  dataset_train = CocoDataset()
  conf = config.TrainConfig()
  
  dataset_train.load_coco(dataset_dir, "train", year=year, auto_download=True)
  if year in '2014':
      dataset_train.load_coco(dataset_dir, "valminusminival", year=year, auto_download=True)
  dataset_train.prepare()
  print(dataset_train.class_names)

  # Validation dataset
  dataset_val = CocoDataset()
  val_type = "val" if year in '2017' else "minival"
  dataset_val.load_coco(dataset_dir, val_type, year=year, auto_download=True)
  dataset_val.prepare()

  # Image Augmentation
  # Right/Left flip 50% of the time
  import imgaug
  augmentation = imgaug.augmenters.Fliplr(0.5)
  
  # Training - Stage 1
  logging.info("Training network heads")
  model.train(dataset_train, dataset_val,
              learning_rate=conf.LEARNING_RATE,
              epochs=10,
              layers='heads',
              augmentation=augmentation)

  # Training - Stage 2
  # Finetune layers from ResNet stage 4 and up
  logging.info("Fine tune Resnet stage 4 and up")
  model.train(dataset_train, dataset_val,
              learning_rate=conf.LEARNING_RATE,
              epochs=10,
              layers='4+',
              augmentation=augmentation)

  # Training - Stage 3
  # Fine tune all layers
  logging.info("Fine tune all layers")
  model.train(dataset_train, dataset_val,
              learning_rate=conf.LEARNING_RATE / 10,
              epochs=10,
              layers='all',
              augmentation=augmentation)
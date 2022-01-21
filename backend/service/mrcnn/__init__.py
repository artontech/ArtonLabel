''' init '''
import logging
import os

from backend import config as options
from .plugin import Plugin

# For tensorflow 2.2:
# CUDA version: 10.1.105_418.96
# cuDNN version: v7.6.5 (November 5th, 2019), for CUDA 10.1
# ===========================================================
# For tensorflow-gpu 2.7: (TODO: bug fix)
# CUDA version: 11.5.0_496.13
# cuDNN version: v8.2.2 (July 6th, 2021), for CUDA 11.4
plugin = None

def init(mode="inference", plugin_name="coco"):
  global plugin
  if mode == "inference" and plugin:
    return
  else:
    release()
  logging.info("Init MaskRCNN, mode=%s, plugin=%s", mode, plugin_name)
  opt = options.get_options()
  plugin = Plugin(mode, plugin_name, opt)

def detect(dataset_dir, image_name):
  # Run detection
  return plugin.detect(dataset_dir, image_name)

def train(dataset_dir):
  plugin.train(dataset_dir)

def release():
  global plugin
  if plugin is None:
    return
  plugin.release()
  plugin = None

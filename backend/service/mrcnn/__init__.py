''' init '''
import logging
import os

from backend import config as options
from .plugin import Plugin

# global variables
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

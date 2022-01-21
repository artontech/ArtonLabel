''' coco config '''
from backend.service.mrcnn.config import Config

class TrainConfig(Config):
  """Configuration for training on MS COCO.
  Derives from the base Config class and overrides values specific
  to the COCO dataset.
  """
  # Give the configuration a recognizable name
  NAME = "coco"

  # We use a GPU with 12GB memory, which can fit two images.
  # Adjust down if you use a smaller GPU.
  GPU_COUNT = 1
  IMAGES_PER_GPU = 2

  # Number of classes (including background)
  NUM_CLASSES = 1 + 80  # COCO has 80 classes

class InferenceConfig(Config):
    NAME = "coco"

    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 80  # COCO has 80 classes

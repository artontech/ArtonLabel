''' router '''
from tornado.web import Application

from backend.controller import error, mrcnn
from backend import config

def make_app():
    ''' make app '''
    options = config.get_options()
    return Application([
        (r"/mrcnn", mrcnn.MrcnnWebSocket),
        (r"/mrcnn/detect", mrcnn.Detect, dict(name="mrcnn detect")),
        (r"/mrcnn/train", mrcnn.Train, dict(name="mrcnn train")),

        (r"/", error.NotFound)
    ], **options.settings)

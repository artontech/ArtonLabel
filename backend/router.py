''' router '''
from tornado.web import Application

from backend.controller import (annotation, error, io, mrcnn, workspace)
from backend import config

def make_app():
    ''' make app '''
    options = config.get_options()
    return Application([
        (r"/annotation/load", annotation.Load, dict(name="load annotation")),
        (r"/annotation/loadConfig", annotation.LoadConfig, dict(name="load annotation config")),
        (r"/annotation/loadMask", annotation.LoadMask, dict(name="load mask")),

        (r"/io/file", io.File, dict(name="get file")),
        (r"/io/next", io.Next, dict(name="get prev/next file name")),

        (r"/mrcnn", mrcnn.MrcnnWebSocket),
        (r"/mrcnn/detect", mrcnn.Detect, dict(name="mrcnn detect")),
        (r"/mrcnn/train", mrcnn.Train, dict(name="mrcnn train")),

        (r"/workspace", workspace.WorkspaceWebSocket),
        (r"/workspace/init", workspace.Init, dict(name="workspace init")),
        (r"/workspace/overview", workspace.Overview, dict(name="workspace overview")),

        (r"/", error.NotFound)
    ], **options.settings)

''' annotation '''

import json
import os
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler)
from backend.util import (pic, url)

class Load(DefaultHandler):
    ''' load annotation '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        image_name = self.get_arg("image_name")

        await self.load_executor(workspace, image_name)

    @run_on_executor
    def load_executor(self, workspace, image_name):
        annotation_dir = os.path.join(workspace, "annotation")
        path = os.path.join(annotation_dir, image_name, "annotation.json")
        if not os.path.exists(path):
            self.write_json(err="no_data", data={"file": path}, status_code=206)
            return

        with open(path, 'r') as f:
            result = json.load(f)
        self.write_json(status="success", data=result)

class LoadConfig(DefaultHandler):
    ''' load annotation config '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")

        await self.load_executor(workspace)

    @run_on_executor
    def load_executor(self, workspace):
        path = os.path.join(workspace, "annotation_config.json")
        if not os.path.exists(path):
            default_annotation_config = {
                "classes": [
                    {
                        "name": "unknown",
                        "color": "#000000",
                        "opacityMask": 0.5,
                        "opacityRoi": 0.9
                    }
                ]
            }
            with open(path, 'w') as f:
                json.dump(default_annotation_config, f)

        with open(path, 'r') as f:
            result = json.load(f)
        self.write_json(status="success", data=result)

class LoadMask(DefaultHandler):
    ''' load mask '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        image_name = self.get_arg("image_name")
        mask_name = self.get_arg("mask_name")

        await self.load_mask_executor(workspace, image_name, mask_name)

    @run_on_executor
    def load_mask_executor(self, workspace, image_name, mask_name):
        annotation_dir = os.path.join(workspace, "annotation")
        path = os.path.join(annotation_dir, image_name, mask_name)
        if not os.path.exists(path):
            self.write_json(err="no_data", data={"file": path}, status_code=404)
            return

        with open(path, 'rb') as f:
            data = f.read()
            data = pic.cv2bytes(pic.cv2transparent(pic.bytes2cv(data), 0))

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + url.encode(mask_name))
            self.write(data)

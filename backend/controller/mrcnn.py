''' mrcnn '''

import json
import logging
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.service import (mrcnn)

class MrcnnWebSocket(DefaultWSHandler):
    name = "mrcnn"

    def open(self):
        logging.info("[ws] WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            logging.info("[ws] recv msg=%s", msg_json)
            self.write_json(msg_type="init", status="success", data=None)

    def on_close(self):
        logging.info("[ws] close")


class Detect(DefaultHandler):
    ''' detect '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        image_name = self.get_arg("image_name")
        plugin_name = self.get_arg("plugin_name")

        await self.detect_executor(workspace, image_name, plugin_name)

    @run_on_executor
    def detect_executor(self, workspace, image_name, plugin_name):
        mrcnn.init(mode="inference", plugin_name=plugin_name)
        result = mrcnn.detect(workspace, image_name)
        self.write_json(status="success", data=result)

class Train(DefaultHandler):
    ''' train '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        dataset_dir = self.get_arg("dataset_dir")
        plugin_name = self.get_arg("plugin_name")

        await self.train_executor(dataset_dir)

    @run_on_executor
    def train_executor(self, dataset_dir, plugin_name):
        mrcnn.init(mode="training", plugin_name=plugin_name)
        mrcnn.train_coco(dataset_dir)
        mrcnn.release()
        self.write_json(status="success", data=dataset_dir)

''' workspace '''

import json
import logging
import os

from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.entity.file import FileDO

class WorkspaceWebSocket(DefaultWSHandler):
    name = "workspace"

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


class Init(DefaultHandler):
    ''' init '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")

        await self.init_executor(workspace)

    @run_on_executor
    def init_executor(self, workspace):
        if not os.path.exists(workspace):
            self.write_json(err="no_workspace")
            return
        self.write_json(status="success", data=workspace)


class Overview(DefaultHandler):
    ''' overview '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        page_no = self.get_arg("page_no", 1)
        page_size = self.get_arg("page_size", 15)

        await self.overview_executor(workspace, page_no, page_size)

    @run_on_executor
    def overview_executor(self, workspace, page_no, page_size):
        if not os.path.exists(workspace):
            self.write_json(err="no_workspace")
            return
        source_dir = os.path.join(workspace, "source")
        file_list = os.listdir(source_dir)
        result_list = []
        total = len(file_list)
        page_end = page_no * page_size
        page_start = page_end - page_size
        for i in range(total):
            if i < page_start or i >= page_end:
                continue

            obj = FileDO()
            obj.none()
            obj.fullname = file_list[i]
            obj.type = "file"
            obj.icon = self.static_url("image.png")
            obj.name, obj.ext = os.path.splitext(file_list[i])
            obj.tags = []
            result_list.append(obj)

        self.write_json(status="success", data={"list": result_list, "total": total})

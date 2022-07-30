''' io '''

import os

from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler)
from backend.util import (pic, url)

NEED_TRANS_PNG = [
    ".tif",
    ".tiff",
]

class File(DefaultHandler):
    ''' get file '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        filename = self.get_arg("filename")

        await self.file_executor(workspace, filename)

    @run_on_executor
    def file_executor(self, workspace, filename):
        source_dir = os.path.join(workspace, "source")
        path = os.path.join(source_dir, filename)
        f_ext = os.path.splitext(filename)[1].lower()
        if not os.path.exists(path):
            self.write_json(err="no_data", data={"file": path}, status_code=404)
            return

        with open(path, 'rb') as f:
            data = f.read()

            if f_ext in NEED_TRANS_PNG:
                data = pic.cv2bytes(pic.bytes2cv(data), ".png")

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + url.encode(filename))
            self.write(data)


class Next(DefaultHandler):
    ''' get prev/next file name '''

    def data_received(self, chunk):
        pass

    async def get(self):
        ''' get '''
        await self.post()

    async def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        filename = self.get_arg("filename")

        await self.overview_executor(workspace, filename)

    @run_on_executor
    def overview_executor(self, workspace, filename):
        source_dir = os.path.join(workspace, "source")
        if not os.path.exists(source_dir):
            self.write_json(err="no_source")
            return
        f_list = os.listdir(source_dir)

        f_idx = f_list.index(filename)
        result = {
            "prev": f_list[f_idx - 1] if f_idx > 0 else None,
            "next": f_list[f_idx + 1] if f_idx + 1 < len(f_list) else None
        }
        self.write_json(status="success", data=result)

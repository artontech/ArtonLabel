''' io '''

import logging
import os

from backend.controller.default import (DefaultHandler)
from backend.util import (url)

class File(DefaultHandler):
    ''' get file '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        workspace = self.get_arg("workspace")
        filename = self.get_arg("filename")

        source_dir = os.path.join(workspace, "source")
        path = os.path.join(source_dir, filename)
        if not os.path.exists(path):
            self.write_json(err="no_data", data={"file": path}, status_code=404)
            return

        with open(path, 'rb') as f:
            data = f.read()

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + url.encode(filename))
            self.write(data)

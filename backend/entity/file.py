''' file '''
from backend.entity.default import DefaultDO

class FileDO(DefaultDO):
    id = None
    name = ""
    ext = ""

    # viewer
    icon = ""
    thumb = ""
    tags = []
    type = "file"

    def none(self):
        ''' clear '''
        super().none()

        self.id = None
        self.name = None
        self.ext = None

        # viewer
        self.icon = None
        self.thumb = None
        self.tags = None
        self.type = None

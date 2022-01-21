''' json encoder '''

import json
import datetime

from backend.entity.default import DefaultDO


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

class DefaultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return DateEncoder.default(self, obj)

        elif isinstance(obj, DefaultDO):
            return obj.__dict__

        else:
            return json.JSONEncoder.default(self, obj)

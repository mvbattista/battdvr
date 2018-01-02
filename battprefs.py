import json
import os

class BattPrefs(object):
    def __init__(self, appname):
        self.appname = appname

    def _get_prefs(self):
        result = {}
        possible_conf_locations = [
            os.path.join(os.path.expanduser('~'), '.config', self.appname, 'config'),
            os.path.join(os.path.expanduser('~'), '.config', self.appname + '.conf')
        ]
        found_conf_loc = None
        for loc in possible_conf_locations:
            if os.path.isfile(loc):
                found_conf_loc = loc
                break
        if found_conf_loc:
            with open(found_conf_loc, 'r') as f:
                full_result = f.read()
            result = json.loads(full_result)
        return result

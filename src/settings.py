try:
    from .settings_local import *
except ImportError:
    raise Exception("settings_local.py does not exist")

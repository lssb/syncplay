import os
from urllib.parse import urlparse

from syncplay import constants
from syncplay import utils


def is_strm_path(file_path):
    if not file_path:
        return False
    path = str(file_path)
    if "://" in path:
        path = urlparse(path).path
    return os.path.splitext(path)[1].lower() == ".strm"


def _canonical_filename(path):
    if utils.isURL(path):
        return path
    return os.path.basename(path)


def add_strm_sidecar_script(args):
    from syncplay.utils import findResourcePath
    sidecar = findResourcePath("strm-sidecars.lua")
    if os.path.isfile(sidecar):
        args["scripts_append"] = sidecar
    return args


class StrmIdentityTracker:
    def __init__(self, timeout=None, time_fn=None):
        self.timeout = constants.STRM_RESOLVE_TIMEOUT if timeout is None else timeout
        self._time = time_fn
        self.source = None
        self.resolved_path = None
        self.source_time = None

    def _now(self):
        if self._time is None:
            import time
            return time.time()
        return self._time()

    def clear(self):
        self.source = None
        self.resolved_path = None
        self.source_time = None

    def begin_open(self, file_path):
        self.clear()
        if is_strm_path(file_path):
            self.source = file_path
            self.source_time = self._now()

    def _resolution_timed_out(self):
        if self.source_time is None:
            return True
        return self._now() - self.source_time > self.timeout

    def canonicalize(self, filename, path):
        if not path:
            return filename, path, None

        if is_strm_path(path):
            self.source = path
            self.resolved_path = None
            self.source_time = self._now()
            return _canonical_filename(path), path, 0

        if self.source:
            if self.resolved_path is None:
                if self._resolution_timed_out():
                    self.clear()
                elif utils.isURL(path):
                    self.resolved_path = path
                    path = self.source
                    return _canonical_filename(path), path, 0
                else:
                    self.clear()
            elif path == self.resolved_path:
                path = self.source
                return _canonical_filename(path), path, 0
            else:
                self.clear()

        if utils.isURL(path):
            filename = path
        return filename, path, None

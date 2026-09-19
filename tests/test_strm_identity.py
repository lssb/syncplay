import os
import unittest

from syncplay.constants import STREAM_ADDITIONAL_IGNORE_TIME, STRM_RESOLVE_TIMEOUT
from syncplay.strm import StrmIdentityTracker, decide_sidecar_load, extra_open_ignore_time


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def time(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class StrmIdentityTrackerTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.tracker = StrmIdentityTracker(time_fn=self.clock.time)

    def test_timeout_constant_is_25_seconds(self):
        self.assertEqual(STRM_RESOLVE_TIMEOUT, 25)

    def test_resolved_url_within_timeout_keeps_strm_identity(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        self.tracker.begin_open(strm_path)
        self.clock.advance(19)
        filename, path, size = self.tracker.canonicalize(
            "video.mkv",
            "http://192.168.193.180:5211/api/strm/play/show.mkv",
        )
        self.assertEqual(filename, os.path.basename(strm_path))
        self.assertEqual(path, strm_path)
        self.assertEqual(size, 0)

    def test_resolved_url_after_timeout_drops_strm_identity(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        url = "http://192.168.193.180:5211/api/strm/play/show.mkv"
        self.tracker.begin_open(strm_path)
        self.clock.advance(25.1)
        filename, path, size = self.tracker.canonicalize("video.mkv", url)
        self.assertEqual(filename, url)
        self.assertEqual(path, url)
        self.assertIsNone(size)

    def test_url_just_inside_25_seconds_still_keeps_identity(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        self.tracker.begin_open(strm_path)
        self.clock.advance(25)
        filename, path, size = self.tracker.canonicalize(
            "video.mkv",
            "http://192.168.193.180:5211/api/strm/play/show.mkv",
        )
        self.assertEqual(filename, os.path.basename(strm_path))
        self.assertEqual(path, strm_path)
        self.assertEqual(size, 0)

    def test_player_reported_strm_path_then_url_keeps_identity(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        filename, path, size = self.tracker.canonicalize("show S06E01.strm", strm_path)
        self.assertEqual(filename, os.path.basename(strm_path))
        self.assertEqual(path, strm_path)
        self.assertEqual(size, 0)
        self.clock.advance(19)
        filename, path, size = self.tracker.canonicalize(
            "video.mkv",
            "http://192.168.193.180:5211/api/strm/play/show.mkv",
        )
        self.assertEqual(filename, os.path.basename(strm_path))
        self.assertEqual(path, strm_path)
        self.assertEqual(size, 0)

    def test_bound_url_stays_mapped_after_timeout(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        url = "http://192.168.193.180:5211/api/strm/play/show.mkv"
        self.tracker.begin_open(strm_path)
        self.clock.advance(5)
        self.tracker.canonicalize("video.mkv", url)
        self.clock.advance(40)
        filename, path, size = self.tracker.canonicalize("video.mkv", url)
        self.assertEqual(filename, os.path.basename(strm_path))
        self.assertEqual(path, strm_path)
        self.assertEqual(size, 0)

    def test_different_local_file_clears_identity(self):
        strm_path = r"Z:\litepan\strm\115\show S06E01.strm"
        self.tracker.begin_open(strm_path)
        filename, path, size = self.tracker.canonicalize("other.mkv", r"D:\videos\other.mkv")
        self.assertEqual(filename, "other.mkv")
        self.assertEqual(path, r"D:\videos\other.mkv")
        self.assertIsNone(size)


class SidecarLoadDecisionTest(unittest.TestCase):
    def test_first_start_on_strm_wrapper_waits(self):
        action, key = decide_sidecar_load(
            r"Z:\show S06E01.strm",
            r"Z:\show S06E01.strm",
            None,
        )
        self.assertEqual(action, "wait")
        self.assertIsNone(key)

    def test_inner_url_after_wrapper_loads(self):
        action, key = decide_sidecar_load(
            r"Z:\show S06E01.strm",
            "http://nas/play/show.mkv",
            None,
        )
        self.assertEqual(action, "load")
        self.assertIsNotNone(key)

    def test_same_inner_file_does_not_reload(self):
        _, key = decide_sidecar_load(r"Z:\show S06E01.strm", "http://nas/a.mkv", None)
        action, key2 = decide_sidecar_load(r"Z:\show S06E01.strm", "http://nas/a.mkv", key)
        self.assertEqual(action, "skip")
        self.assertEqual(key, key2)

    def test_switching_to_another_strm_loads_again(self):
        _, key = decide_sidecar_load(r"Z:\a.strm", "http://nas/a.mkv", None)
        action, key2 = decide_sidecar_load(r"Z:\b.strm", "http://nas/b.mkv", key)
        self.assertEqual(action, "load")
        self.assertNotEqual(key, key2)

    def test_url_without_playlist_path_waits(self):
        action, key = decide_sidecar_load(None, "http://nas/a.mkv", None)
        self.assertEqual(action, "wait")
        self.assertIsNone(key)


class ExtraOpenIgnoreTimeTest(unittest.TestCase):
    def test_strm_uses_resolve_timeout(self):
        self.assertEqual(
            extra_open_ignore_time(r"Z:\show S06E01.strm"),
            STRM_RESOLVE_TIMEOUT,
        )

    def test_http_url_uses_stream_ignore(self):
        self.assertEqual(
            extra_open_ignore_time("http://nas/play/show.mkv"),
            STREAM_ADDITIONAL_IGNORE_TIME,
        )

    def test_local_video_has_no_extra_ignore(self):
        self.assertEqual(extra_open_ignore_time(r"D:\videos\show.mkv"), 0)


class MpvStartupScriptTest(unittest.TestCase):
    def test_mpv_startup_appends_strm_sidecar_script(self):
        from syncplay.strm import add_strm_sidecar_script
        args = add_strm_sidecar_script({})
        sidecar = args["scripts_append"].replace("\\", "/")
        self.assertTrue(sidecar.endswith("resources/strm-sidecars.lua"))
        self.assertTrue(os.path.isfile(args["scripts_append"]))


if __name__ == "__main__":
    unittest.main()

"""Regression checks for the small static media lists; no network or packages."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from build import render_clips, render_tracks
from check import Page


class MediaTests(unittest.TestCase):
    def render(self, function, entries):
        with patch.object(Path, "read_text", return_value=json.dumps(entries)):
            return function()

    def test_gallery_can_grow_beyond_four_entries(self):
        text = self.render(render_clips, [{"game": f"Test game {i}"} for i in range(12)])
        page = Page(text)
        self.assertEqual(len(page.find("figure")), 12)
        self.assertEqual(page.errors, [])
        self.assertNotIn("iframe", text)
        self.assertEqual(page.refs, [])

    def test_youtube_link_is_static_with_click_to_play_metadata(self):
        text = self.render(render_clips, [{"game": "Test game", "title": "Test clip",
            "youtube_id": "TEST_ID_123", "thumbnail": "/assets/images/test.webp",
            "thumbnail_alt": "A test thumbnail", "date": "2000-01-01", "caption": "Test caption"}])
        page = Page(text)
        self.assertEqual(page.find("a")[0]["href"], "https://www.youtube.com/watch?v=TEST_ID_123")
        self.assertEqual(page.find("a")[0]["data-youtube"], "TEST_ID_123")
        self.assertEqual(page.find("img")[0]["loading"], "lazy")
        self.assertEqual(page.find("time")[0]["datetime"], "2000-01-01")
        self.assertEqual(page.find("iframe"), [])
        self.assertEqual(page.errors, [])

    def test_other_video_hosts_keep_an_ordinary_link(self):
        text = self.render(render_clips, [{"game": "Test game", "url": "https://example.com/clip"}])
        page = Page(text)
        self.assertEqual(page.find("a")[0]["href"], "https://example.com/clip")
        self.assertNotIn("data-youtube", page.find("a")[0])

    def test_plain_text_fields_are_escaped(self):
        text = self.render(render_clips, [{"game": 'Test "game"', "title": "<script>test</script>",
            "url": "https://example.com/clip", "caption": "<img src=x>"}])
        page = Page(text)
        self.assertEqual(page.find("script"), [])
        self.assertEqual(page.find("img"), [])
        self.assertIn("&lt;script&gt;", text)

    def test_invalid_links_ids_and_remote_thumbnails_fail_the_build(self):
        for fields in [{"url": "javascript:alert(1)"}, {"youtube_id": "invalid"},
                       {"thumbnail": "https://example.com/remote.jpg"}, {"date": "not-a-date"}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.render(render_clips, [{"game": "Test game", **fields}])

    def test_tracks_are_links_with_optional_notes_and_no_player(self):
        text = self.render(render_tracks, [{"title": "Test piece", "artist": "Test composer",
            "url": "https://example.com/music", "note": "<Test note>"}, {"title": "Another piece"}])
        page = Page(text)
        self.assertEqual(len(page.find("li")), 2)
        self.assertEqual(page.find("a")[0]["href"], "https://example.com/music")
        self.assertIn("&lt;Test note&gt;", text)
        self.assertEqual(page.find("audio") + page.find("iframe"), [])
        self.assertNotIn("TODO", text)
        self.assertEqual(page.errors, [])


if __name__ == "__main__":
    unittest.main()

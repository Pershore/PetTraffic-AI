import unittest
from unittest.mock import patch
from email.utils import format_datetime
from datetime import datetime, timezone

from topic_radar import clean_link, fetch


class TopicRadarTests(unittest.TestCase):
    def test_clean_link_removes_tracking_query_and_fragment(self):
        self.assertEqual(
            clean_link("https://example.lt/story?id=42&utm_source=news#comments"),
            "https://example.lt/story",
        )

    def test_clean_link_keeps_path_and_host(self):
        self.assertEqual(
            clean_link("https://news.example.lt/a/b/"),
            "https://news.example.lt/a/b/",
        )

    @patch("topic_radar.urlopen")
    def test_fetch_parses_rss_and_normalizes_date(self, mocked_urlopen):
        published = format_datetime(datetime(2026, 11, 11, 6, 0, tzinfo=timezone.utc))
        xml = f"""<?xml version="1.0"?>
        <rss version="2.0"><channel><item>
          <title>Šuns priežiūra &amp; sveikata</title>
          <link>https://example.lt/story?utm_source=rss</link>
          <source>Veterinarijos naujienos</source>
          <pubDate>{published}</pubDate>
        </item></channel></rss>""".encode()
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return xml
        mocked_urlopen.return_value = Response()

        result = fetch("šunų priežiūra")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Šuns priežiūra & sveikata")
        self.assertEqual(result[0]["link"], "https://example.lt/story")
        self.assertEqual(result[0]["source"], "Veterinarijos naujienos")
        self.assertEqual(result[0]["published"], "2026-11-11")

    @patch("topic_radar.urlopen", side_effect=TimeoutError("timeout"))
    def test_fetch_handles_feed_failure(self, _mocked_urlopen):
        self.assertEqual(fetch("kačių priežiūra"), [])


if __name__ == "__main__":
    unittest.main()

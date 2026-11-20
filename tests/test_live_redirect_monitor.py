"""Tests for live verification of retired-article redirects."""

from email.message import Message
from io import BytesIO
from urllib.error import HTTPError
from unittest.mock import patch
import unittest

from agent.check_live_site import NoRedirectHandler, fetch_redirect
from agent.validate_site import REQUIRED_RETIRED_ARTICLE_REDIRECTS


class FakeOpener:
    def __init__(self, error):
        self.error = error

    def open(self, request, timeout):
        raise self.error


class LiveRedirectMonitorTests(unittest.TestCase):
    def test_live_monitor_covers_all_twenty_retired_url_variants(self):
        self.assertEqual(len(REQUIRED_RETIRED_ARTICLE_REDIRECTS), 20)

    def test_fetch_redirect_returns_first_301_location_without_following(self):
        headers = Message()
        headers["Location"] = "/articles/kada-kreiptis-i-veterinara"
        error = HTTPError(
            "https://pettraffic-ai.pages.dev/articles/old.html",
            301,
            "Moved Permanently",
            headers,
            BytesIO(b""),
        )
        with patch("agent.check_live_site.build_opener", return_value=FakeOpener(error)):
            status, location = fetch_redirect("https://pettraffic-ai.pages.dev/articles/old.html")
        self.assertEqual(status, 301)
        self.assertEqual(location, "/articles/kada-kreiptis-i-veterinara")

    def test_redirect_handler_does_not_follow_redirects(self):
        handler = NoRedirectHandler()
        result = handler.redirect_request(None, None, 301, "Moved Permanently", {}, "https://example.com/next")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

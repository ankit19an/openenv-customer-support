import unittest

from server import render_homepage


class TestServerHomepage(unittest.TestCase):
    def test_homepage_contains_live_sections(self):
        page = render_homepage()

        self.assertIn("Customer Support RL Env", page)
        self.assertIn("Scenario Deck", page)
        self.assertIn("/docs", page)
        self.assertIn("/reset?task_name=easy", page)
        self.assertIn("API Surface", page)


if __name__ == "__main__":
    unittest.main()

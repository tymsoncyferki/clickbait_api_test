import unittest

from utils import matches_pattern, get_configuration_name
from config import ConfName

class TestUtils(unittest.TestCase):

    def test_wildcard_match(self):
        self.assertTrue(matches_pattern("*www.thesun.co.uk/*/", "https://www.thesun.co.uk/money/"))
        self.assertFalse(matches_pattern("*www.thesun.co.uk/*/*/", "https://www.thesun.co.uk/money/"))
        self.assertFalse(matches_pattern("*www.thesun.co.uk/*/", "https://www.thesun.co.uk/money/32089637/cheapest-place-/"))

    def test_conf_getter(self):
        self.assertEqual(get_configuration_name("www.google.com/search?"), ConfName.GOOGLE)

if __name__ == "__main__":
    unittest.main()

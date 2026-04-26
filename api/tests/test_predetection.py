import unittest

from predetection import run_detection

class TestGoogle(unittest.IsolatedAsyncioTestCase):

    async def test_google_detect(self):
        with open("test_files/trump_google.html", 'rb') as file:
            html = file.read()
        response = await run_detection(str(html))
        self.assertEqual(len(response.predictions.keys()), 9)

    async def test_google_thesun(self):
        with open("test_files/thesun.html", 'rb') as file:
            html = file.read()
        response = await run_detection(str(html))
        print(len(response.predictions.keys()))
        self.assertGreater(len(response.predictions.keys()), 50)

if __name__ == "__main__":
    unittest.main()

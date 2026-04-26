import unittest

from prediction import get_probability_of_clickbait_title, return_embeddings_chat
from prediction_async import get_embeddings, predict_titles_async

class TestPredictionMethods(unittest.TestCase):

    def test_request(self):
        self.assertEqual(len(return_embeddings_chat("sample text")), 1000)

    def test_probability_prediction(self):
        pred = get_probability_of_clickbait_title("Sample Title Man")
        self.assertGreater(pred, 0)
        self.assertLess(pred, 1)

class TestAsyncPredictionMethods(unittest.TestCase):

    async def test_get_embeddings(self):
        embs = await get_embeddings(["marek", "jarek", "sth"])
        self.assertEqual(len(embs), 3)
        self.assertEqual(len(embs[0]), 1000)

    async def test_predictions(self):
        predictions = await predict_titles_async({"fb/s.pl41241": "sample title", "anotherlink.pl": "watch this man"})
        self.assertEqual(len(predictions.keys()), 2)
        self.assertGreater(predictions["anotherlink.pl"], 0)


if __name__ == "__main__":
    unittest.main()

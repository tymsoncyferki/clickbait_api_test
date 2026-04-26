import unittest

from measure import *

class TestHelperFunctions(unittest.TestCase):
    
    def test_remove_punctuation(self):
        self.assertEqual(remove_punctuation("Hello, world!"), "Hello world")

    def test_cut_value(self):
        self.assertEqual(cut_value(1.5), 1)
        self.assertEqual(cut_value(0.5), 0.5)
        self.assertEqual(cut_value(-0.5), 0)

    def test_calculate_metrics(self):
        metrics = calculate_metrics("Watch this women grow hair on her eyes [Tweets]")
        self.assertEqual(len(metrics), len(METRICS_FUNCTIONS) + 1)

class TestMeasuresFunctions(unittest.TestCase):

    def test_words_count(self):
        self.assertEqual(words_count("Hello world"), 2)

    def test_common_words_ratio(self):
        self.assertAlmostEqual(common_words_ratio("On it is wonderful"), 3/4)

    def test_capital_letters_ratio(self):
        self.assertAlmostEqual(capital_letters_ratio("HELLOworld"), 5/10)

    def test_capital_words_count(self):
        self.assertEqual(capital_words_count("Hello World HERE"), 1)

    def test_nonclickbait_punctuation_count(self):
        self.assertEqual(nonclickbait_punctuation_count("Hello, world."), 2)

    def test_clickbait_punctuation_count(self):
        self.assertEqual(clickbait_punctuation_count("Hey, What?!"), 2)

    def test_numbers_count(self):
        self.assertEqual(numbers_count("$450 123 PLN100"), 2)

    def test_pronouns_2nd_person_count(self):
        self.assertEqual(pronouns_2nd_person_count("You are amazing, but he is not"), 1)

    def test_superlatives_ratio(self):
        self.assertEqual(superlatives_ratio("This is the best book"), 1)

    def test_speculatives_count(self):
        self.assertEqual(speculatives_count("Donald Trump might be gay"), 1)

    def test_baiting_words_count(self):
        self.assertEqual(baiting_words_count("People who dance are slimmer"), 1)

    def test_polarity_score(self):
        self.assertLess(polarity_score("I hate this"), 0)

    def test_subjectivity_score(self):
        self.assertGreater(subjectivity_score("I love this"), 0.3)

    def test_flesch_reading_ease_score(self):
        self.assertGreater(flesch_reading_ease_score("This is a simple sentence."), 70)

if __name__ == "__main__":
    unittest.main()
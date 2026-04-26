import string 
import numpy as np
from nltk import pos_tag, word_tokenize
import textstat

import math

from textblob import TextBlob
from config import STOP_WORDS

BAIT_PHRASES = [
 'obsessed',
 'celebrity',
 'anyone',
 'know',
 'af',
 'omg',
 'movies',
 'amazing',
 'totally',
 'video',
 'things',
 'remember',
 'videos',
 'quiz',
 'guess',
 'characters',
 'hilarious',
 'tweets',
 'favorite',
 'products',
 'ways',
 'pictures',
 'photos',
 'based',
 'understand',
 'perfectly',
 'actually',
 'makeup',
 'character',
 'reasons',
 'laugh',
 'nude',
 'nudes',
 'naked',
 'and it',
 'are you',
 'based on',
 'can you',
 'do you',
 'here what',
 'how to',
 'if you',
 'is the',
 'make you',
 'need to',
 'of the',
 'on your',
 'people who',
 'that are',
 'that will',
 'the best',
 'the most',
 'the world',
 'things you',
 'this is',
 'ways to',
 'we know',
 'will make',
 'you will',
 'you need',
 'you are']

""" helper functions """

def is_numeric(s):
    """ returns true if at most one character in the string is non-numeric and all others are numeric """
    non_numeric_count = sum(1 for char in s if not char.isdigit())
    if non_numeric_count == len(s):
        return False
    return non_numeric_count <= 1

def remove_punctuation(text):
    """ removes punctuation """
    return text.translate(str.maketrans('', '', string.punctuation))

""" measures """

def words_count(text):
    """ calculates number of words """
    return len(text.split())

def common_words_ratio(text):
    """ percentage of stop words in text """
    words = word_tokenize(remove_punctuation(text.lower()))
    common_words = [word for word in words if word in STOP_WORDS]
    return len(common_words) / len(words)

def capital_letters_ratio(text):
    """ calculates capital letters ratio """
    text = remove_punctuation(text)
    return sum([char.isupper() for char in list(text)]) / len(text)

def capital_words_count(text):
    """ calculates capital words """
    return sum([1 for word in word_tokenize(text) if word.isupper() and len(word) > 1])

def nonclickbait_punctuation_count(text):
    """ counts non-clickbait related punctuation """
    punctuation = "$%&,.;:-/"
    return sum([1 for x in text if x in punctuation])

def clickbait_punctuation_count(text):
    """ counts clickbait related punctuation, only left brackets as otherwise they would be double calculated """
    punctuation = '!"#(?'
    return sum([1 for x in text if x in punctuation])

def numbers_count(text):
    """ calculates the count of numbers (not digits)"""
    text = remove_punctuation(text)
    return sum([is_numeric(x) for x in word_tokenize(text)])

def pronouns_2nd_person_count(text):
    """ 2nd person pronouns usage """
    second_person_pronouns = ["you", "your", "yours", "yourself", "yourselves"]
    return sum([1 for x in word_tokenize(text.lower()) if x in second_person_pronouns])

def superlatives_ratio(text):
    """ percentage of adjectives and adverbs which are in superlative form """
    tagged_words = pos_tag(word_tokenize(text.lower()))
    adj_adv_count = 0
    superlative_count = 0
    for _, tag in tagged_words:
        if tag in ('JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'):
            adj_adv_count += 1
            if tag in ('JJS', 'RBS'):  # if superlative
                superlative_count += 1
    if adj_adv_count == 0:
        return 0
    return superlative_count / adj_adv_count

def speculatives_count(text):
    """ usage of speculative forms """
    speculative_words = {
        "might", "may", "could", "can", "perhaps", "possibly", "probably", "maybe",
        "seems", "appears", "suggests", "indicates", "likely", "unlikely", "assume"
    }
    return sum([1 for x in word_tokenize(text.lower()) if x in speculative_words])

def baiting_words_count(text):
    """ number of baiting words used """
    return sum([1 for x in BAIT_PHRASES if x in text.lower()])

def polarity_score(text):
    """ polarity score """
    return TextBlob(text).sentiment.polarity

def subjectivity_score(text):
    """ subjectivity score """
    return TextBlob(text).sentiment.subjectivity

def flesch_reading_ease_score(text):
    """ difficulty of the text, if its easy to read or not, the higher the easier
    
    Formula:
    206.835 - 1.015 * (total words / total sentences) - 84.6 (total syllables / total words)

    Scores:
    -90.00  	Very easy to read. Easily understood by an average 11-year-old student.
    90.0-80.0	Easy to read. Conversational English for consumers.
    80.0-70.0	Fairly easy to read.
    70.0-60.0	Plain English. Easily understood by 13- to 15-year-old students.
    60.0-50.0	Fairly difficult to read.
    50.0-30.0	Difficult to read.
    30.0-10.0	Very difficult to read. Best understood by university graduates.
    10.0-   	Extremely difficult to read. Best understood by university graduates.
    source: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    """
    return textstat.flesch_reading_ease(text)


def cut_value(value):
    """ cuts value to (0,1) range """
    if value > 1:
        return 1
    elif value < 0:
        return 0
    return value

def calculate_metrics(text):
    """ calculates all metrics specified in METRICS_FUNCTIONS variable """
    metrics = {}
    for name, function in METRICS_FUNCTIONS.items():
        metrics[name] = function(text)
    baitness = baitness_measure(text, metrics_dict=metrics)
    metrics['baitness'] = baitness
    return metrics

def baitness_measure(text, debug=False, metrics_dict=None):
    """ calculates baitness measure """
    if metrics_dict is not None:
        # Eye-catchingness
        punct_count = metrics_dict["bait_punct"]
        capitals_ratio = metrics_dict["capitals_ratio"] * 3
        number_count = metrics_dict["numbers"]

        # Content curiosity
        pronouns_2_count = metrics_dict["2nd_pronouns"]
        super_count = metrics_dict["superlatives"] * 2
        spec_count = metrics_dict["speculatives"]
        bait_words = metrics_dict["bait_words"]

        # Sentiment - measures high polarity and high subjectivity
        polarity = abs(metrics_dict["polarity"])
        subjectivity = metrics_dict["subjectivity"]

        # Difficulty of reading - reading ease score and common words ratio
        fres = cut_value(metrics_dict["fres"] / 100)
        cw_ratio = cut_value(metrics_dict["cw_percentage"] * 1.5)
    else:
        # eye catchingness
        punct_count = clickbait_punctuation_count(text)
        capitals_ratio = capital_letters_ratio(text) * 3
        number_count = numbers_count(text)
        
        # content curiosity
        pronouns_2_count = pronouns_2nd_person_count(text)
        super_count = superlatives_ratio(text) * 2
        spec_count = speculatives_count(text)
        bait_words = baiting_words_count(text)
        
        # sentiment - measures high polarity and high subjectivity
        polarity = abs(polarity_score(text))
        subjectivity = subjectivity_score(text)

        # difficulty of reading - reading ease score and common words ratio
        fres = cut_value(flesch_reading_ease_score(text) / 100)
        cw_ratio = cut_value(common_words_ratio(text) * 1.5)

    # eye catch
    eye_catch_list = [punct_count, capitals_ratio, number_count]
    eye_catch = cut_value(np.mean(eye_catch_list))
    if debug:
        print(eye_catch_list)
    
    # content curiosity
    curiosity_list = [pronouns_2_count, super_count, spec_count, bait_words]
    curiosity = np.sqrt(cut_value(np.mean(curiosity_list)))
    if debug:
        print(curiosity_list)

    # sentiment - measures high polarity and high subjectivity
    sentiment = math.sqrt(polarity * subjectivity)

    # difficulty of reading - reading ease score and common words ratio
    ease_of_text = np.mean([fres, cw_ratio])

    metric_list = [eye_catch, sentiment, ease_of_text, curiosity]
    measure = np.mean(metric_list)
    if debug:
        print(metric_list)
    
    return measure

def explain_baitness(text, probability, metrics_dict = None):
    """ generates explanation for the prediction """
    if metrics_dict is not None:
        # Eye-catchingness
        punct_count = metrics_dict["bait_punct"]
        capitals_ratio = metrics_dict["capitals_ratio"] * 3
        number_count = metrics_dict["numbers"]

        # Content curiosity
        pronouns_2_count = metrics_dict["2nd_pronouns"]
        super_count = metrics_dict["superlatives"] * 2
        spec_count = metrics_dict["speculatives"]
        bait_words = metrics_dict["bait_words"]

        # Sentiment - measures high polarity and high subjectivity
        polarity = abs(metrics_dict["polarity"])
        subjectivity = metrics_dict["subjectivity"]

        # Difficulty of reading - reading ease score and common words ratio
        fres = cut_value(metrics_dict["fres"] / 100)
        cw_ratio = cut_value(metrics_dict["cw_percentage"] * 1.5)
    else:
        # eye catchingness
        punct_count = clickbait_punctuation_count(text)
        capitals_ratio = capital_letters_ratio(text) * 3
        number_count = numbers_count(text)
        
        # content curiosity
        pronouns_2_count = pronouns_2nd_person_count(text)
        super_count = superlatives_ratio(text) * 2
        spec_count = speculatives_count(text)
        bait_words = baiting_words_count(text)
        
        # sentiment - measures high polarity and high subjectivity
        polarity = abs(polarity_score(text))
        subjectivity = subjectivity_score(text)

        # difficulty of reading - reading ease score and common words ratio
        fres = cut_value(flesch_reading_ease_score(text) / 100)
        cw_ratio = cut_value(common_words_ratio(text) * 1.5)

    primary_metrics = {
        "2nd person pronouns": pronouns_2_count,
        "capital words": capitals_ratio, 
        "numbers": number_count,
        "punctuation": punct_count,
        "bait words": bait_words,
        "superlatives": super_count,
        "speculatives": spec_count,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "common words": cw_ratio / 1.5,
        "reading ease": (fres / 2) ** 2  # its usually higher than other metrics, so we scale it down a little bit
    }

    sorted_metrics = sorted(primary_metrics.items(), key=lambda x: x[1], reverse=True)

    explanations = {
        "2nd person pronouns": "uses second person pronouns",
        "capital words": "uses many capital letters",
        "numbers": "uses numbers to draw attention",
        "punctuation": "uses clickbait-specific punctuation",
        "bait words": "includes clickbait-specific words",
        "superlatives": "uses superlative words",
        "speculatives": "uses speculative words",
        "polarity": "has a strong emotional tone",
        "subjectivity": "is highly subjective",
        "common words": "uses common words frequently",
        "reading ease": "is very easy to read"
    }

    # print(np.sqrt(baitness_measure(text)))
    if probability > 0.6:
        top_contributors = sorted_metrics[:2]
        explanation = ", ".join([explanations[metric] for metric, _ in top_contributors])
    elif probability > 0.4:
        explanation = explanations[sorted_metrics[0][0]]
    else:
        explanation = "no grounds to classify as a clickbait"
    
    return explanation

METRICS_FUNCTIONS = {
    "n_words": words_count,
    "cw_percentage": common_words_ratio,
    "capitals_ratio": capital_letters_ratio,
    "capitals_count":capital_words_count,
    "bait_punct": clickbait_punctuation_count,
    "nonbait_punct": nonclickbait_punctuation_count,
    "numbers": numbers_count,
    "2nd_pronouns": pronouns_2nd_person_count,
    "superlatives": superlatives_ratio,
    "speculatives": speculatives_count,
    "bait_words": baiting_words_count,
    "polarity": polarity_score,
    "subjectivity": subjectivity_score,
    "fres": flesch_reading_ease_score
}

def get_baitness_scaled(title):
    """ baitness scaled to typical probability range - optimal cutoff changed from 0.3 to ~0.5 """
    return np.sqrt(baitness_measure(title))
import trafilatura
from bs4 import BeautifulSoup

from dtos import HTMLPayload, Article, PredictionResponse
from measure import explain_baitness, calculate_metrics
from prediction import get_probability_of_clickbait_title
from spoiling import get_spoiler
from config import logger

# extraction 

def extract_content(html_content: str) -> str:
    """
    extracts the main content from the HTML string using trafilatura

    Args:
        html_content (str): raw HTML content from a webpage

    Returns:
        str: extracted main content of the page
    """
    main_content = trafilatura.extract(html_content)
    if main_content is None:
        main_content = ""
    return main_content

def extract_title(html_content: str) -> str:
    """
    extracts the title from the h1 tag in the HTML content

    Args:
        html_content (str): raw HTML content from a webpage

    Returns:
        str: extracted title
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    h1_tag = soup.find('h1')
    title = ''
    if h1_tag:
        title = h1_tag.get_text(strip=True)
    logger.info(f"post-detection title (repr): {title!r}")
    return title

def predict(title: str, content: str, metrics_dict: dict = None) -> float:
    """
    wrapper for calculating clickbait probability

    Args:
        title (str): title of the article
        content (str): article content
        metrics_dict (dict): precalculated metrics

    Returns:
        float: the probability of the title being clickbait
    """
    return get_probability_of_clickbait_title(title, metrics_dict=metrics_dict)

def explain(title: str, content: str, probability: float, metrics_dict: dict = None) -> str:
    """
    wrapper for explaining clickbait prediction

    Args:
        title (str): title of the article
        content (str): article content
        probability (float): probability of clickbait
        metrics_dict (dict): precalculated metrics

    Returns:
        str: generated explanation
    """
    return explain_baitness(title, probability, metrics_dict=metrics_dict)

def spoil(title: str, content: str, prediction: int) -> str:
    """
    wrapper for spoiling

    Args:
        title (str): title of the article
        content (str): content of the webpage
        prediction (int): 

    Returns:
        str: generated spoiler
    """
    if prediction == 0:
        return ""
    spoiler = get_spoiler(title, content)
    return spoiler

# functions to be imported into api

def handle_extract(payload: HTMLPayload) -> Article:
    """
    Extracts title and main content from the provided HTML 

    Args:
        payload (HTMLPayload): payload with raw html content

    Returns:
        Article: payload containing the title and main content
    """
    html_content = payload.html
    title = extract_title(html_content)
    main_content = extract_content(html_content)
    return Article(title=title, content=main_content)

def handle_predict(payload: Article, generate_spoiler=True) -> PredictionResponse:
    """
    makes a clickbait prediction for the given article

    Args:
        payload (Article): payload containing the title and content of the article

    Returns:
        PredictionResponse: response containing the prediction, probability, explanation, and spoiler
    """
    if len(payload.title) == 0:
        return PredictionResponse(prediction=0, probability=0, explanation="no article title on this page", spoiler="")
    metrics_dict = calculate_metrics(payload.title)
    probability = predict(payload.title, payload.content, metrics_dict=metrics_dict)
    prediction = 1 if probability > 0.5 else 0
    explanation = explain(payload.title, payload.content, probability, metrics_dict=metrics_dict)
    if generate_spoiler:
        spoiler = spoil(payload.title, payload.content, prediction=prediction)
    else:
        spoiler = ""
    return PredictionResponse(prediction=prediction, probability=round(probability, 2), explanation=explanation, spoiler=spoiler)

def handle_extract_and_predict(payload: HTMLPayload, generate_spoiler=True) -> PredictionResponse:
    """
    extracts title and main content and makes a prediction

    Args:
        payload (HTMLPayload): payload with raw html content

    Returns:
        PredictionResponse: response containing the prediction, probability, explanation, and spoiler
    """
    article = handle_extract(payload)
    prediction_response = handle_predict(payload=article, generate_spoiler=generate_spoiler)
    logger.info(f"{prediction_response}")
    return prediction_response

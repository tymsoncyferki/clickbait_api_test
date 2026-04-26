from typing import Any

from openai import OpenAI

from config import Config, MODEL, logger
from measure import calculate_metrics

def send_request(prompt: str):
    """
    sends request to OpenAI embeddings endpoint

    Args:
        prompt (str): input text for generating embeddings

    Returns:
        dict: response from API
    """
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    res = client.embeddings.create(
        input=prompt,
        model="text-embedding-3-large",
        dimensions=1000
    )
    return res

def return_embeddings_chat(prompt: str, max_retries: int = 2) -> list:
    """
    gets OpenAI embeddings for a given text prompt

    Args:
        prompt (str): the input text for generating embeddings

    Returns:
        list: embedding vector
    """
    res = "default blank response"
    attempt = 0
    while attempt < max_retries:
        try:
            res = send_request(prompt)
            returned_data = res.data
            logger.info("Request to OpenAI Embeddings API was successfull")
            return returned_data[0].embedding
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"There is a problem with a request to OpenAI: {e}, {res}, aborting prediction")
                raise ValueError(f"There is a problem with connection to OpenAi Embeddings API")
            attempt += 1
    return []


def get_probability_of_clickbait_title(title: str, metrics_dict: dict | None = None, model: Any = MODEL):
    """
    makes prediction for a title using a pretrained model

    Args:
        title (str): title to predict
        metrics_dict (dict, optional): a dictionary of precomputed metrics for the title, if None calculated on the spot
        model (Any): pretrained model used for prediction

    Returns:
        float: probability of the title being clickbait
    """
    # get openai embeddings
    input_to_model = return_embeddings_chat(title)

    # calculate metrics if needed
    if metrics_dict is None:
        metrics_dict = calculate_metrics(title)

    # append metrics to model input
    for _, value in metrics_dict.items():
        input_to_model.append(value)

    return model.predict_proba([input_to_model])[0][1]
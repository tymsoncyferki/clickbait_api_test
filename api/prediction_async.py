import asyncio
import aiohttp

from config import Config
from measure import calculate_metrics
from config import MODEL

async def fetch_embedding(session, title: str) -> list | None:
    """
    sends async request to OpenAI embeddings endpoint

    Args:
        prompt (str): input text for generating embeddings

    Returns:
        dict: response from API
    """
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
    }
    payload = {
        "model": "text-embedding-3-large",
        "dimensions": 1000,
        "input": title
    }

    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"][0]["embedding"]
            else:
                error_message = await response.text()
                raise Exception(f"Error {response.status}: {error_message}")
    except Exception as e:
        print(f"error during fetching embedding for title '{title}': {e}")
        return None


async def get_embeddings(titles: list[str]) -> list:
    """
    fetches embeddings for a list of titles asynchronously

    Args:
        titles (list[str]): list of titles

    Returns:
        list: list of embeddings or None for titles that failed
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_embedding(session, title) for title in titles]
        embeddings = await asyncio.gather(*tasks)
        return embeddings

async def predict_titles_async(titles_dict: dict) -> dict:
    """
    generates clickbait predictions

    Args:
        titles_dict (dict): dictionary where keys are links and values are titles

    Returns:
        dict[str, int]: a dictionary where keys are links and values are predictions (1 for clickbait, 0 otherwise)
    """
    predictions = {}
    embeddings = await get_embeddings(titles_dict.values())
    for link, title, emb in zip(list(titles_dict.keys()), list(titles_dict.values()), embeddings):
        metrics_dict = calculate_metrics(title)
        for _, value in metrics_dict.items():
            emb.append(value)
        prob = MODEL.predict_proba([emb])[0][1]
        # predictions[link] = 1 if prob > 0.5 else 0
        predictions[link] = float(prob)
    return predictions

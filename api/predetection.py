from bs4 import BeautifulSoup

from dtos import HTMLPayload, DetectionResponse, ConfName
from utils import get_configuration_name, get_domain
from prediction_async import predict_titles_async
from config import logger

async def run_google_detection(html_content: str) -> DetectionResponse:
    soup = BeautifulSoup(html_content, 'html.parser')
    titles = {}
    for result in soup.find_all('div', {'class': 'MjjYud'}):
        anchors = result.find_all('a')
        for anchor in anchors:
            title_tag = anchor.find('h3')
            if title_tag is not None:
                title = title_tag.text
                link = anchor.get('href')
                titles[link] = title
    predictions = await predict_titles_async(titles)
    logger.info(f"google pre-click predictions: {len(predictions.keys())}")
    return DetectionResponse(predictions=predictions)

async def run_thesun_detection(html_content: str) -> DetectionResponse:
    soup = BeautifulSoup(html_content, 'html.parser')
    titles = {}
    containers = []
    class_names = ['site-content']
    for name in class_names:
        containers.extend(soup.find_all('div', {'class': name}))
    for result in containers:
        anchors = result.find_all('a')
        for anchor in anchors:
            # if anchor.has_attr('data-headline'):
            #     title = anchor.get('data-headline')
            #     link = anchor.get('href')
            #     if len(title) > 0:
            #         titles[link] = title
            logger.info(f"{anchor.get('href')}")
            headline_tag = anchor.find('h3', class_='story__headline')
            if headline_tag:
                title = headline_tag.get_text(strip=True)
                link = anchor.get('href')
                logger.info(f"title {title}")
                if title and link and link not in titles.keys():
                    logger.info("Adding to list")
                    titles[link] = title

    predictions = await predict_titles_async(titles)
    logger.info(f"the sun pre-click predictions: {len(predictions.keys())}")
    return DetectionResponse(predictions=predictions)

async def run_detection(html_content: str, url: str = None) -> DetectionResponse:
    """ universal function """
    soup = BeautifulSoup(html_content, 'html.parser')
    titles = {}
    containers = soup.find_all('body')
    for result in containers:
        anchors = result.find_all('a')
        for anchor in anchors:
            headline_tag = anchor.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headline_tag:
                title = headline_tag.get_text(strip=True)
                link = anchor.get('href')
                if title and link and link not in titles.keys():
                    titles[link] = title

    predictions = await predict_titles_async(titles)
    logger.info(f"{get_domain(url) if url else ""} pre-click predictions: {len(predictions.keys())}")
    for link, prob in predictions.items():
        logger.info(f"pre-detection prediction: title={titles.get(link)!r} prob={prob}")
    return DetectionResponse(predictions=predictions)

# async def handle_predetection(payload: HTMLPayload) -> DetectionResponse:
#     conf_name = get_configuration_name(payload.url)
#     if conf_name == ConfName.GOOGLE:
#         return await run_google_detection(payload.html)
#     elif conf_name == ConfName.THESUN:
#         return await run_thesun_detection(payload.html)
#     return DetectionResponse(predictions={})

async def handle_predetection(payload: HTMLPayload) -> DetectionResponse:
    return await run_detection(html_content=payload.html, url=payload.url)
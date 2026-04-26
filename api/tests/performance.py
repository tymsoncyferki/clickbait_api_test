import time
from predetection import run_google_detection
from postdetection import handle_extract_and_predict
from dtos import HTMLPayload
import numpy as np
from tqdm import tqdm

async def test_predetection():
    with open("test_files/thesun.html", 'rb') as file:
        html = file.read()

    the_sun_times = []
    google_times = []

    for i in tqdm(range(20)):
        
        # start_time = time.time()
        # await handle_thesun_detection(str(html))
        # end_time = time.time()
        # the_sun_times.append(end_time - start_time)

        start_time = time.time()
        await run_google_detection(str(html))
        end_time = time.time()
        google_times.append(end_time - start_time)

    all_times = the_sun_times + google_times
    mean_time = np.mean(all_times)
    std_time = np.std(all_times)
    median_time = np.median(all_times)
    min_time = min(all_times)
    max_time = max(all_times)

    print(f"avg: {round(mean_time, 3)}s, std: {round(std_time, 3)}s, median: {round(median_time, 3)}, min: {round(min_time, 3)}, max: {round(max_time, 3)}")

# asyncio.run(main())

def test_postdetection():
    with open("test_files/pinterest.html", 'rb') as file:
        html = file.read()

    all_times = []
    for i in tqdm(range(20)):

        start_time = time.time()
        handle_extract_and_predict(HTMLPayload(url="asdf", html=str(html)), generate_spoiler=False)
        end_time = time.time()
        all_times.append(end_time - start_time)

    mean_time = np.mean(all_times)
    std_time = np.std(all_times)
    median_time = np.median(all_times)
    min_time = min(all_times)
    max_time = max(all_times)

    print(f"avg: {round(mean_time, 3)}s, std: {round(std_time, 3)}s, median: {round(median_time, 3)}, min: {round(min_time, 3)}, max: {round(max_time, 3)}")

test_postdetection()
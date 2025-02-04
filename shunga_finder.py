import asyncio
import os
from pathlib import Path

import httpx
import browser_cookie3
import bs4
from tqdm import tqdm

EXPECTED_IMAGS_PER_PAGE = 25

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)


def is_page_exists(page: int) -> bool:
    return (data_dir / f"page_{page}.html").exists()

def is_img_ids_exists(page: int):
    return (data_dir / f"page_{page}.img_ids").exists()


async def process(client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore) -> None:
    async with sem:
        if is_page_exists(page):
            print(f"Page {page} already exists")
            page += 1
            return

        URL = "https://seiga.nicovideo.jp/shunga/list"

        r = await client.get(URL, params={
            'page': page,
            'sort': 'image_created',
        })
        if r.status_code != 200:
            print("page", page, "ERROR: status_code:", r.status_code)
            return

        # .illust_list_img

        soup = bs4.BeautifulSoup(r.content, "html.parser")
        imgs = soup.select(".illust_list_img")
        if len(imgs) != EXPECTED_IMAGS_PER_PAGE:
            print(f"Page {page} has {len(imgs)} images, expected {EXPECTED_IMAGS_PER_PAGE}")
            return

        with open(data_dir / f"page_{page}.html.cache", "wb") as f:
            f.write(r.content)

        os.rename(data_dir / f"page_{page}.html.cache", data_dir / f"page_{page}.html")

        print(f"Saved page {page}")
        return


def get_page_image_ids(page: int) -> list[int]:
    with open(data_dir / f"page_{page}.html", "rb") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")

    imgs = soup.select(".illust_list_img")
    """
<div class="illust_list_img ">
<div class="center_img  center_img_size_160"><a class="center_img_inner "
        href="https://seiga.nicovideo.jp/seiga/im11552990"><img
            src="https://lohas.nicoseiga.jp/thumb/11552990q?1737461779" alt=""><span
            class="center_img_spring">&nbsp;</span></a></div>
<div class="illust_title">
    <p class="thumb_title"><a href="/seiga/im11552990">じゅん</a></p>
</div>
<div class="summary_container">
    <div class="summary ">
        <p class="thumb_summary">なつい </p>
    </div>
</div>
<div class="counter_info">閲覧：10 コメ：1 クリップ：0</div>
</div>
"""
    pure_ids = []
    if is_img_ids_exists(page):
        with open(data_dir / f"page_{page}.img_ids", "r") as f:
            for line in f:
                pure_ids.append(int(line.strip()))
            return pure_ids
    
    for img in imgs:
        a = img.select_one("a")
        href = a["href"]
        img_id = href.split("/")[-1]
        assert img_id.startswith("im")
        pure_id = img_id[2:]
        pure_ids.append(int(pure_id))

    with open(data_dir / f"page_{page}.img_ids.cache", "w") as f:
        for img_id in pure_ids:
            f.write(str(img_id) + "\n")

    os.rename(data_dir / f"page_{page}.img_ids.cache", data_dir / f"page_{page}.img_ids")
    
    return pure_ids


async def main() -> None:
    sess = httpx.AsyncClient(timeout=20)
    sess.cookies.update(browser_cookie3.firefox())
    sess.headers.update({
        'User-Agent': 'Mozilla/5.0 (saveweb; STWP) saveweb/0.1',
    })

    # https://seiga.nicovideo.jp/shunga/list?page=2&sort=image_created_a

    MAX_PAGE = 20

    sem = asyncio.Semaphore(20)
    tasks = [process(sess, page, sem) for page in range(1, MAX_PAGE+1)]
    await asyncio.gather(*tasks)

    all_img_ids = []
    for page in tqdm(range(1, MAX_PAGE+1), desc="extracting image ids"):
        if not is_page_exists(page):
            continue

        img_ids = get_page_image_ids(page)
        all_img_ids.extend(img_ids)

    print("Total images:", len(all_img_ids))
    all_img_ids = sorted(all_img_ids)
    with open(data_dir / "all_img_ids.txt", "w") as f:
        for img_id in all_img_ids:
            f.write(str(img_id) + "\n")
        

if __name__ == "__main__":
    asyncio.run(main())

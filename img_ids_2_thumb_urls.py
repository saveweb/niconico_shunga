with open("data/all_img_ids.txt") as f:
    img_ids = [int(line) for line in f]


with open("data/img_ids_2_thumb_urls.txt", "w") as f:
    for img_id in img_ids:
        f.write(f"https://lohas.nicoseiga.jp/thumb/{img_id}l\n")

with open("data/img_ids_2_ori_urls.txt", "w") as f:
    for img_id in img_ids:
        f.write(f"https://seiga.nicovideo.jp/image/source/{img_id}\n")


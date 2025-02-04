with open("data_merged/all_img_ids.txt") as f:
    img_ids = [int(line) for line in f]
img_ids = list(set(img_ids))
img_ids = sorted(img_ids)
for imgid in img_ids:
    print(f"https://seiga.nicovideo.jp/seiga/im{imgid}")
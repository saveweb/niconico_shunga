import requests

sess = requests.Session()

# https://lohas.nicoseiga.jp/thumb/11552125{a..z}

result = []
for magic_char in range(ord('a'), ord('z')+1):
    url = f'https://lohas.nicoseiga.jp/thumb/11552125{chr(magic_char)}'
    r = sess.get(url)
    if r.status_code == 200:
        result.append((magic_char, len(r.content), url))
        print(chr(magic_char), len(r.content), r.url)


print('Best thumb:', max(result, key=lambda x: x[1]))

result = sorted(result, key=lambda x: x[1])
for r in result:
    print(r)

# l is the best thumb
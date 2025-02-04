import logging
import os
import httpx

# set logger format
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)
client = httpx.Client(timeout=20, follow_redirects=True, headers={
    "User-Agent": "Mozilla/5.0 (saveweb; STWP) saveweb/0.1"
})
def login_impl(username, password):
    # clear cookies
    client.cookies.clear()

    logger.info("Logging in as %s", username)

    root = "https://account.nicovideo.jp"
    response = client.get(root + "/login?site=seiga")
    page = response.text

    data = {
        "mail_tel": username,
        "password": password,
    }
    # url = root + text.unescape(text.extr(page, '<form action="', '"'))
    url = root + page.split('<form action="')[1].split('"')[0]
    logger.info("url: %s", url)
    response = client.post(url, data=data)

    logger.info("response.url: %s", response.url)
    if "message=cant_login" in str(response.url):
        raise Exception("AuthenticationError")

    if "/mfa" in str(response.url):
        logger.info("mfa in response.url")
        page = response.text
        # email = text.extr(page, 'class="userAccount">', "<")
        email = page.split('class="userAccount">')[1].split("<")[0]
        code = input(f"Email Confirmation Code ({email}): ")

        data = {
            "otp": code,
            "loginBtn": "Login",
            "device_name": "saveweb",
        }
        # url = root + text.unescape(text.extr(page, '<form action="', '"'))
        url = root + page.split('<form action="')[1].split('"')[0]
        # response = self.request(url, method="POST", data=data)
        response = client.post(url, data=data)

        if not response.history and \
                b"Confirmation code is incorrect" in response.content:
            # raise exception.AuthenticationError(
            #     "Incorrect Confirmation Code")
            raise Exception("Incorrect Confirmation Code")

    # return {
    #     cookie.name: cookie.value
    #     for cookie in self.cookies
    #     if cookie.expires and cookie.domain == self.cookies_domain
    # }
    logger.info("cookies: %s", client.cookies)
    return True

def get_ori_image_url(client: httpx.Client, image_id: int):
    """Get url for an image with id 'image_id'"""
    url = f"https://seiga.nicovideo.jp/image/source/{image_id}"
    response = client.head(
        url, follow_redirects=False)
    location = response.headers["location"]
    if "nicovideo.jp/login" in location:
        raise Exception(
            "HTTP redirect to login page (%s)", location.partition("?")[0])
    return location.replace("/o/", "/priv/", 1)

COOKIES_DOMAIN = ".nicovideo.jp"
def dump_cookie_jar(cilent: httpx.Client):
    with open("cookie_jar.txt", "w") as f:
        cookies = client.cookies.jar
        for cookie in cookies:
            if cookie.domain != COOKIES_DOMAIN:
                continue
            f.write(f"{cookie.name}={cookie.value}\n")
def load_cookie_jar(client: httpx.Client):
    if not os.path.exists("cookie_jar.txt"):
        return False
    with open("cookie_jar.txt", "r") as f:
        for line in f:
            name, value = line.strip().split("=")
            client.cookies.set(name, value, domain=COOKIES_DOMAIN)
    return True

def login():
    ok = load_cookie_jar(client) or login_impl(input("ACC:"), input("PWD:"))
    assert ok, "Login failed"

def main():
    login()
    image_id = 482486
    ori_image_url = get_ori_image_url(client, image_id)
    logger.info("ori_image_url: %s", ori_image_url)

if __name__ == "__main__":
    main()
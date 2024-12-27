import base64
import json
import time
import urllib

import bs4
import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import schedule


def login(session, config):
    login_url = r"https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Felife.fudan.edu.cn%2Flogin2.action"
    response = session.get(login_url)

    xml = bs4.BeautifulSoup(response.text, "html.parser")
    desired_names = {"lt", "dllt", "execution", "_eventId", "rmShown"}
    values = {
        input_tag["name"]: input_tag["value"]
        for input_tag in xml.find_all("input")
        if "name" in input_tag.attrs and input_tag["name"] in desired_names
    }

    data = {
        "username": config["user"]["username"],
        "password": config["user"]["password"],
    }

    data.update(values)

    response = session.post(login_url, data=data)


def get_resource_id(session, config):
    respose = session.get(
        f"https://elife.fudan.edu.cn/public/front/getResource2.htm?contentId={config['order']['contentId']}&ordersId=&currentDate={config['order']['date']}"
    )

    bs4_object = bs4.BeautifulSoup(respose.text, "html.parser")
    resources = bs4_object.findAll("tr", class_="site_tr")

    for resource in resources:
        if resource.find("td", {"class": "site_td4"}) is None:
            continue
        if (
            resource.find("td", {"class": "site_td1"}).find("font").string
            == config["order"]["time"]
        ):
            return (
                resource.find("td", {"class": "site_td5"})
                .find("select")["id"]
                .replace("orderCount", "")
            )


def captcha(text, base64, config):
    response = requests.post(
        "https://upload.chaojiying.net/Upload/Processing.php",
        data={
            "softid": config["chaojiying"]["softid"],
            "user": config["chaojiying"]["username"],
            "pass2": config["chaojiying"]["pass2"],
            "codetype": "9501",
            "file_base64": base64,
        },
    )
    json = response.json()
    pic_str = json["pic_str"]
    result = pic_str.split("|")
    result_map = {}
    for item in result:
        result_map[item.split(",")[0]] = item.split(",")[1].rjust(3, "0") + item.split(
            ","
        )[2].rjust(3, "0")

    print(result_map)
    code = ""
    for i in text:
        code += result_map[i]
    return code


def RSA_encrypt(text):
    key = RSA.import_key(
        r"""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCOrdWTLglhdgMDUIIaDoQI9IWp
+S0elwYsy8P5luxbAL5SkohMO4lrwz1Ji0zPCa5nLXZ1CC8xYh6u/TBbdG7YWDqO
rj5eR+e3UmDuj0t3j2XZwp+/R7WICydgzu89e4ZtDQly72rtziWGqbCyg7LG5lpv
el1ejKJocJgYJE7WxQIDAQAB
-----END PUBLIC KEY-----"""
    )

    cipher = PKCS1_v1_5.new(key)
    return base64.b64encode(cipher.encrypt(text.encode("utf-8"))).decode("utf-8")


def order(session, resource_id, config):
    order_page_url = f"https://elife.fudan.edu.cn/public/front/loadOrderForm_ordinary.htm?serviceContent.id={config['order']['contentId']}&serviceCategory.id={config['order']['categoryId']}&codeStr=&currentDate={config['order']['date']}&resourceIds={resource_id}&orderCounts=1"
    response = session.get(
        order_page_url,
    )

    bs4_object = bs4.BeautifulSoup(response.text, "html.parser")
    rsa_text_ = bs4_object.find("input", {"id": "rsa_text_"})["value"]
    order_user = bs4_object.find("input", {"id": "order_user"})["value"]
    mobile = bs4_object.find("input", {"id": "mobile"})["value"]

    while True:
        response = session.get(
            "https://elife.fudan.edu.cn/public/front/getClickValidateImg.htm",
            headers={"Referer": order_page_url},
        )
        json = response.json()
        text = json["object"]["ValidText"]
        img = json["object"]["ValidImage"]

        try:
            code = captcha(text, img, config)
        except:
            continue

        response = session.post(
            "https://elife.fudan.edu.cn/public/front/validateClickCode.htm",
            headers={"Referer": order_page_url},
            data={"code": code},
        )

        if response.json()["object"]["IsSuccess"]:
            print("验证通过")
            break

    text_ = urllib.parse.quote_plus(
        f"{rsa_text_}_{RSA_encrypt(f"FuDan_{int(time.time() *1000)}")}"
    )

    result = session.post(
        "https://elife.fudan.edu.cn/public/front/saveOrderForCGYY.htm?op=order",
        data={
            "moveEnd_X": None,
            "wbili": None,
            "validateCode": code,
            "serviceContent.id": config["order"]["contentId"],
            "serviceCategory.id": config["order"]["categoryId"],
            "contentChild": None,
            "codeStr": None,
            "itemsPrice": None,
            "acceptPrice": None,
            "orderuser": order_user,
            "rsa_text_": rsa_text_,
            "text_": text_,
            "resourceIds": resource_id,
            "orderCounts": 1,
            "lastDays": 0,
            "mobile": mobile,
            "d_cgyy.bz": None,
        },
        headers={"Referer": order_page_url},
    )

    print(result.text)


def order_stadium(config):
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36",
        }
    )

    login(session, config)
    resource_id = get_resource_id(session, config)
    order(session, resource_id, config)


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    order_stadium(config)

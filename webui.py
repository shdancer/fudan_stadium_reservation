import json
import threading
import traceback
import streamlit as st
from order import order_stadium
from auto import auto

import time

st.title("自动预约系统")

st.write("## Step 0: 计算超级鹰密码的md5值")

with st.form("md5"):
    password = st.text_input("超级鹰密码", type="password")
    submitted = st.form_submit_button("计算")

    if submitted:
        import hashlib

        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        st.write(m.hexdigest())
        st.success("计算完成")

st.write("## Step 1: 配置信息")


try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        "user": {
            "username": "",
            "password": "",
        },
        "order": {
            "date": f"{time.strftime('%Y-%m-%d')}",
            "time": "",
            "contentId": "",
            "categoryId": "",
        },
        "chaojiying": {
            "username": "",
            "pass2": "",
            "softid": "",
        },
        "auto": {
            "time": "",
        },
    }


with st.form("config_form"):
    username = st.text_input("学号", value=config["user"]["username"])
    password = st.text_input("密码", type="password", value=config["user"]["password"])
    date = st.text_input("日期", value=config["order"]["date"])
    time_ = st.text_input("时间", value=config["order"]["time"])
    contentId = st.text_input("内容id", value=config["order"]["contentId"])
    categoryId = st.text_input("类别id", value=config["order"]["categoryId"])

    chaojiying_username = st.text_input(
        "超级鹰用户名", value=config["chaojiying"]["username"]
    )
    chaojiying_password = st.text_input(
        "超级鹰密码（复制计算的md5码到这里）",
        type="password",
        value=config["chaojiying"]["pass2"],
    )
    chaojiying_softid = st.text_input(
        "超级鹰softid", value=config["chaojiying"]["softid"]
    )

    submitted = st.form_submit_button("保存配置信息")

    if submitted:
        config["user"]["username"] = username
        config["user"]["password"] = password
        config["order"]["date"] = date
        config["order"]["time"] = time_
        config["order"]["contentId"] = contentId
        config["order"]["categoryId"] = categoryId
        config["chaojiying"]["username"] = chaojiying_username
        config["chaojiying"]["pass2"] = chaojiying_password
        config["chaojiying"]["softid"] = chaojiying_softid
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        st.rerun()
        st.success("保存成功")


st.write("## Step 2: 开始预约")


def run_auto(config):
    try:
        auto(config)
    except Exception as e:
        tb_str = traceback.format_exc()
        st.session_state.error_message = tb_str

    if not st.session_state.error_message:
        st.session_state.auto_success = True


if "error_message" not in st.session_state:
    st.session_state.error_message = None

if "auto_success" not in st.session_state:
    st.session_state.auto_success = False

with st.form("order"):
    auto_time = st.text_input("自动预约时间")

    submitted_now = st.form_submit_button("开始马上预约")
    submitted_time = st.form_submit_button("开始自动预约")
    if submitted_now:
        try:
            order_stadium(config)
        except Exception as e:
            tb_str = traceback.format_exc()
            st.session_state.error_message = tb_str

        if not st.session_state.error_message:
            st.session_state.auto_success = True

    if submitted_time:
        config["auto"]["time"] = auto_time
        threading.Thread(target=run_auto, args=(config,)).start()
        st.success("开始自动预约，在后台运行...")

st.write("## Step 3: 预约结果")
st.write("自动预约暂不支持查看预约结果，可以在后台查看")
if st.session_state.error_message:
    st.error(f"错误信息： {st.session_state.error_message}")
    st.session_state.error_message = None

if st.session_state.auto_success:
    st.success("预约成功")
    st.session_state.auto_success = False

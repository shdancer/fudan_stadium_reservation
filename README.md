# 自动预约系统

本脚本针对Fudan的场馆预约，逆向了场馆预约前端，实现了无需浏览器即可预约场馆，空出计算机使用。

## 设置

本脚本给出了`config.json.example`，将其改为`config.json`并填入对应信息即可开始预约。

## 运行
安装依赖后，运行命令
```
python auto.py
```
即可开始等待预约。

## TODO
- [ ] 添加报错和预约成功
- [ ] cv验证码识别pipeline（考虑到验证码背景数量很少，可以多次获取验证码然后得到背景可以较为轻松ocr）
- [ ] 写一个GUI

## 声明

本脚本目的是研究和学习前端技术和爬虫技术，**请勿用于实际用途**。

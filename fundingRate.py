import requests
import schedule
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json

secret = json.load(open('secret.json'))
sender = secret["email"]["sender"]
receivers = secret["email"]["receivers"]
username = secret["email"]["username"]
password = secret["email"]["password"]

def sendmsg(text):
    params = {
        "corpid": secret["weixin"]['corpid'],
        "corpsecret": secret["weixin"]['corpsecret']
    }
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    r = requests.get(url, params = params)
    access_token = r.json()["access_token"]
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
    params = {
        "access_token": access_token
    }
    data = {
        "touser": "@all",
        "msgtype" : "text",
        "agentid" : secret["weixin"]['agentid'],
        "text" : {
            "content" : text
        }
    }
    r = requests.post(url, params = params, json = data)

def send_email(text):
    print("send_email")
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = ",".join(receivers)
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.163.com', 465)
        #smtpObj.set_debuglevel(1)
        smtpObj.login(username, password)
        message['Subject'] = "永续合约资费报告"
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        smtpObj.close()
    except Exception as e:
        print("Send Mail Fail", e)


def job(FR_trigger, alertType):
    coinglassSecret = secret["coinglassSecret"]
    try:
        url = "https://open-api.coinglass.com/public/v2/funding"
        headers = {
            "accept": "application/json",
            "coinglassSecret": coinglassSecret
        }
        
        alert = []
        response = requests.get(url, headers=headers)

        for i in response.json()["data"]:
            #print("symbol", i["symbol"])
            #print("USDT-SWAP:")
            for j in i["uMarginList"]:
                if j["status"] == 0:
                    continue
                if j["status"] == 1:
                    if abs(j["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USDT", "e": j["exchangeName"], "r": j["rate"], "n": None})
                if j["status"] == 2:
                    if abs(j["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USDT", "e": j["exchangeName"], "r": j["rate"], "n": j["predictedRate"]})
            #print("\nCOIN-SWAP:")
            for k in i["cMarginList"]:
                if k["status"] == 0:
                    continue
                if k["status"] == 1:
                    if abs(k["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USD", "e": k["exchangeName"], "r": k["rate"], "n": None})
                if k["status"] == 2:
                    if abs(k["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USD", "e": k["exchangeName"], "r": k["rate"], "n": k["predictedRate"]})
            #print("------")

        alert.sort(key=lambda x: x["r"], reverse=True)
        alert = list(filter(lambda x: x["e"] in ["Binance", "OKX"], alert))
        if len(alert) == 0:
            return

        # EMAIL 通知
        text = ""
        text += str(len(alert)) + " coins FR above " + str(FR_trigger) + "\n" + "\n"
        for i in alert:
            text += format(i["r"], "+.2f") + " " + ((format(i["n"], "+.2f")) if i["n"] else "     ") + " " + '{0:<7}'.format(i["s"]) + '{0:<8}'.format(i["e"] ) + " " + i["u"] + "\n"
            #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text)
            #print(format(i["r"], "+.2f") + "%" + " " + '{0:<7}'.format((format(i["n"], "+.2f") if i["n"] else "") + "%") + '{0:<7}'.format(i["e"] ) + " " + '{0:<6}'.format(i["s"]) + " " + '{0:<4}'.format(i["u"]))
        text +=  "\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        
        if "email" in alertType:
            print(text)
            send_email(text)

        # 微信通知
        text = ""
        text += str(len(alert)) + " 个币合约资费超过 " + str(FR_trigger) + "\n"
        for i in alert:
            text += "品种: " + i["s"] + "\n"
            text += "饺易所: " + i["e"] + "\n"
            text += "当前资费: " + format(i["r"], "+.2f") + "\n"
            text += "下期资费: " + (format(i["n"], "+.2f") if i["n"] else "无") + "\n"
            text += "类型: " + i["u"] + "\n"
            text += "时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + "\n"
        if "weixin" in alertType:
            print(text)
            sendmsg(text)
    except Exception as e:
        print(e)
        pass

job(0.5, "weixin")
job(0.1, "email")
schedule.every().hour.do(lambda: job(0.1, "email"))
schedule.every().hour.do(lambda: job(0.5, "weixin"))
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "starting")
while True:
    schedule.run_pending()
    time.sleep(1)
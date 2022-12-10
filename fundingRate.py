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

coinglassSecret = secret["coinglassSecret"]
def job():
    try:
        url = "https://open-api.coinglass.com/public/v2/funding"
        headers = {
            "accept": "application/json",
            "coinglassSecret": coinglassSecret
        }
        FR_trigger = 0.1
        alert = []
        response = requests.get(url, headers=headers)

        for i in response.json()["data"]:
            #print("symbol", i["symbol"])
            #print("USDT-SWAP:")
            for j in i["uMarginList"]:
                if j["status"] == 0:
                    break
                if j["status"] == 1:
                    if abs(j["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USDT", "e": j["exchangeName"], "r": j["rate"], "n": None})
                if j["status"] == 2:
                    if abs(j["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USDT", "e": j["exchangeName"], "r": j["rate"], "n": j["predictedRate"]})
            #print("\nCOIN-SWAP:")
            for k in i["cMarginList"]:
                if k["status"] == 0:
                    break
                if k["status"] == 1:
                    if abs(k["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USD", "e": k["exchangeName"], "r": k["rate"], "n": None})
                if k["status"] == 2:
                    if abs(k["rate"]) > FR_trigger:
                        alert.append({"s": i["symbol"], "u": "USD", "e": k["exchangeName"], "r": k["rate"], "n": k["predictedRate"]})
            #print("------")

        alert.sort(key=lambda x: x["r"], reverse=True)

        text = ""
        text += datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        for i in alert:
            text += format(i["r"], "+.2f") + "," + ((format(i["n"], "+.2f")) if i["n"] else "     ") + "," + i["s"] + "," + i["e"] + "," + i["u"] + "\n"
            #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text)
            #print(format(i["r"], "+.2f") + "%" + " " + '{0:<7}'.format((format(i["n"], "+.2f") if i["n"] else "") + "%") + '{0:<7}'.format(i["e"] ) + " " + '{0:<6}'.format(i["s"]) + " " + '{0:<4}'.format(i["u"]))
        send_email(text)
    except Exception as e:
        pass
#job()
schedule.every().hour.do(job)
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "starting")
while True:
    schedule.run_pending()
    time.sleep(1)
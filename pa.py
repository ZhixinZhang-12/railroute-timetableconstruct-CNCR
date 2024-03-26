import requests
import json

def getTraincode():
    apiurl = "https://api.rail.re/train/G46"

    response = requests.get(url=apiurl)

    if response.status_code == 200:  # 检查响应状态
        marList = response.json()  # 解析JSON响应

        if len(marList) <= 1:
            pass
        else:
            marshalling = marList[0].get("emu_no")  # 提取POI信息
            print(marshalling[0:-4])

    else:
        print("请求失败，状态码：", response.status_code)

src="a"
route1=f"{src} "
print(route1)

'''

'''

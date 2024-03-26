import requests
import json

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


'''

[{"date":"2021-01-19","emu_no":"CRH380B3720","train_no":"G236/G233"},{"date":"2021-01-18","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-18","emu_no":"CRH380B3729","train_no":"G236/G233"},{"date":"2021-01-17","emu_no":"CRH380B3645","train_no":"G236/G233"},{"date":"2021-01-16","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-16","emu_no":"CRH380B3729","train_no":"G236/G233"},{"date":"2021-01-15","emu_no":"CRH380B3676","train_no":"G236/G233"},{"date":"2021-01-14","emu_no":"CRH380B3587","train_no":"G236/G233"},{"date":"2021-01-13","emu_no":"CRH380B3676","train_no":"G236/G233"},{"date":"2021-01-12","emu_no":"CRH380B3753","train_no":"G236/G233"},{"date":"2021-01-11","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-11","emu_no":"CRH380B3663","train_no":"G236/G233"},{"date":"2021-01-09","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-09","emu_no":"CRH380B3663","train_no":"G236/G233"},{"date":"2021-01-08","emu_no":"CRH380B3604","train_no":"G236/G233"},{"date":"2021-01-07","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-05","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-04","emu_no":"CRH380B3591","train_no":"G236/G233"},{"date":"2021-01-04","emu_no":"CRH380B3642","train_no":"G236/G233"},{"date":"2021-01-03","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2021-01-02","emu_no":"CRH380B3611","train_no":"G236/G233"},{"date":"2021-01-02","emu_no":"CRH380B3676","train_no":"G236/G233"},{"date":"2021-01-01","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2020-12-31","emu_no":"CRH380B3591","train_no":"G236/G233"},{"date":"2020-12-30","emu_no":"CRH380B3614","train_no":"G236/G233"},{"date":"2020-12-29","emu_no":"CRH380B3591","train_no":"G236/G233"},{"date":"2020-12-28","emu_no":"CRH380B3729","train_no":"G236/G233"},{"date":"2020-12-27","emu_no":"CRH380B3591","train_no":"G236/G233"},{"date":"2020-12-26","emu_no":"CRH380B3663","train_no":"G236/G233"},{"date":"2020-12-26","emu_no":"CRH380B3720","train_no":"G236/G233"}]

'''

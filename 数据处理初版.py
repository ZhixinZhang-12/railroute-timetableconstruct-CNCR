<<<<<<< HEAD

import pandas
import numpy
import datetime
import random
import networkx
desired_caps = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '9',  # 手机安卓版本
    'deviceName': 'xxx',  # 设备名，安卓手机可以随意填写

    'appPackage': 'tv.danmaku.bili',  # 启动APP Package名称
    'appActivity': '.MainActivityV2',  # 启动Activity名称

    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App
    'newCommandTimeout': 6000,
    'automationName': 'UiAutomator2'
    # 'app': r'd:\apk\bili.apk',
}
# {
#   "platformName": "Android",
#   "platformVersion": '9',
#   "deviceName": "xxx",
#   "appPackage": "",
#   "appActivity": ". ",
#   "unicodeKeyboard": True,
#   "reseteyboard": True,
#   "noReset": True,
#   "newCommandTimeout": 6000,
#   "automationName" :"UiAutomator2"
# }

# 读取文件，设置列名便于后续操作

species = {'新空调普快': ['120', 'LPPPPPP', 0], '新空调快速': ['120', 'LPPPPPP', 0],
           '新空调特快': ['140', 'LPPPPPP', 0], '新空调直快': ['160', 'LPPPPPP', 0],
           '动车': ['200', 'LPPL', 1], '城际': ['200', 'LPPL', 1], '高速': ['300', 'LPPLLPPL', 2]}
species1 = {'K': ['120', 'LPPPPPP', 0], 'T': ['140', 'LPPPPPP', 0], 'Z': ['160', 'LPPPPPP', 0],
            'D': ['200', 'LPPL', 1], 'C': ['200', 'LPPL', 1], 'G': ['300', 'LPPLLPPL', 2]}

# 车站-编号,掉向,用时以及运行车辆种类映射关系
# 图片左(0)右(1)侧线路key值相同则掉向,
# 国铁车辆行走左侧,2为数据为左侧股道编号
# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
station = {
    '京济联络线济南方向': ['b', 0, 2, 1, 8], '济郑高速长清方向': ['c', 0, 2, 1, 7],
    '济南西站': ['d', -1, 0, 0, 7], '济南西动车所': ['e', -1, 0, 0, 30],
    '京沪高速德州东方向': ['f', 1, '1', '2', 6, ], '京沪高速泰安站方向': ['a', 0, 2, 1, 7, ],
    '石济客专齐河方向': ['g', 1, 1, 2, 6], '石济客专济南东方向': ['h', 1, 1, 2, 6, ],
}

# orient="index", columns=["车站编号", "车站所在侧", "进场股道", "离场股道", "到达中心时间"]

# 线路和车站关系，主要用于从车站-值获取线路-键
route1 = {
    '济南西动车所': ["济南西"], '京济联络线济南方向': ["济南"], '济郑高速长清方向': ["长清"],
    '京沪高速泰安站方向': ["泰安", "曲阜东", "滕州东", "枣庄", "徐州东", "宿州东", "蚌埠南", "南京南"],
    '京沪高速德州东方向': ["北京南", "天津西", "天津", "沧州西", "德州东"],
    '石济客专齐河方向': ["齐河", "禹城东", "平原东"], '石济客专济南东方向': ["济南东"]}
# 两个合在一起写太难看




def dealTime(datafr: pandas.DataFrame) -> pandas.DataFrame:
    # 对于始发车和终到车进行时间处理，默认相同
    for idx, row in datafr.iterrows():
        if row["到时"] == "--:--":
            row["到时"] = row["开时"]
        elif row["开时"] == "--:--":
            row["开时"] = row["到时"]
    # 计算停站时间
    datafr["到时"] = pandas.to_datetime(datafr["到时"])
    datafr["开时"] = pandas.to_datetime(datafr["开时"])
    # 实发终到设置停站时间
    # pd["停站时间"].replace(0,10,inplace=True)

    return datafr


def stopStTime(stopTime: pandas.Timedelta) -> int:
    a = int(stopTime.seconds/60)  # 处理为数值类型的分钟时间
    # 始发或是终到的时间是随机的
    return a if a > 0 else random.randint(10, 30)


def ModtimeStr(switchTime: pandas.Timestamp) -> str:
    # 处理为仅有时分秒样式的字符串格式的时间
    return switchTime.strftime("%H:%M:%S")


def speMarType(traincode: str) -> str:  # 目前获取编组信息的方式
    til = species1[traincode[0]]  # 处理获取车辆信息字符串部分
    return "{cod} COMMUTER {speed} {mar} X1".format(cod=traincode, speed=til[0], mar=til[1])


def checkin(entrance: str) -> int:
    # 终到车
    res = 0
    if entrance == "无检票口信息":
        res = 0
    else:  # 检票口15A 非终到车
        res = int(entrance.strip("检票口AB"))
    return res


# 'D1636 COMMUTER 200 LPPL X1 : b#2#10:27:00#0 d#17#10:35:00#2 g#2#10:43:00#0 ',


def prevnextST(stopSt: list[str], stIdx: int) -> list[str]:
    # 返回结果，获取目标车站的前后车站
    res = ["", ""]
    res1 = ["", ""]
    if stIdx == 0:  # 始发车视为始发车站和下一站
        res = [stopSt[0], stopSt[1]]
    elif stIdx == len(stopSt)-1:  # 终到车视为前一站和终到站
        res = [stopSt[len(stopSt)-2], stopSt[len(stopSt)-1]]
    else:  # 中间站
        res = [stopSt[stIdx-1], stopSt[stIdx+1]]
    # 判断并修改进路
    for k, v in route1.items():
        if res[0] in v:
            res1[0] = k
        elif res[1] in v:
            res1[1] = k
    return res1


def arrLeaTime(t1: pandas.Timestamp, st: list[str], mark: int) -> str:
    tarst = st[mark]
    useTime = station[tarst][4]
    if mark == 0:  # 进场
        res = t1-datetime.timedelta(minutes=useTime)
    else:
        res = t1+datetime.timedelta(minutes=useTime)
    return res.strftime("%H:%M:%S")


'''
a={'G2664,蚌埠南,19:50到,19:54开,检票口检票口1,\n', 'G2664,济南西,21:39到,--:--开,无检票口信息,\n', 'G2664,合肥,18:50到,19:12开,无检票口信息,\n', 'G2664,六安,18:08到,18:10开,检票口二层检票口,\n', 'G2664,汉口,--:--到,16:48开,检票口二楼B6,\n', 'G2664,徐州东,20:31到,20:36开,检票口东广场进站7A7B检票,\n'}
f =open(file="ltInfo.txt", mode="w", encoding="utf-8")
for it in a:
    it=it.replace("到","").replace("开","")
    f.write(it)
f.close()

'''


def processTrains(fn: str, targetSt: str) -> pandas.DataFrame:
    # 处理产生初步所需信息的数据框
    trainsFrame = pandas.read_csv(filepath_or_buffer=fn,
                                  sep=",", encoding="utf8", header=None)
    trainsFrame.columns = ["车次",  "停站", "到时", "开时", "检票口", "drop1"]
    trainsFrame.drop(columns=["drop1"], inplace=True)

    trainsFrame = dealTime(trainsFrame)  # 初步处理时间
    trainsFrame.sort_values(by=["车次", "到时"], inplace=True)  # 归类排序
    # 整理为分钟样式的停站时间
    #trainsFrame["停站时间"] = trainsFrame["停站时间"].apply(lambda x: stopStTime(x))
    trainsFrame.reset_index(drop=True, inplace=True)
    # 按照车次分组为列表，同时车次不作为索引以便于操作
    tfgp = trainsFrame.groupby(by=["车次"], as_index=False).agg(list)
    # 获取目标停站的索引值，设置为一个辅助列
    tfgp["auxIdx"] = tfgp['停站'].apply(lambda x: x.index(targetSt))

    # 获取前后停站以得到更好的交路映射
    tfgp["目标前后站"] = tfgp.apply(
        lambda x: prevnextST(x["停站"], x["auxIdx"]), axis=1)
    # 获取其他信息
    tfgp["目标站到时"] = tfgp.apply(lambda x: x["到时"][x["auxIdx"]], axis=1)
    tfgp["目标站开时"] = tfgp.apply(lambda x: x["开时"][x["auxIdx"]], axis=1)
    tfgp["目标站检票口"] = tfgp.apply(lambda x: x["检票口"][x["auxIdx"]], axis=1)

    # 提取需要的信息为新的dataframe
    trainInfoNeed = tfgp[["车次", "目标站到时", "目标站开时", "目标站检票口", "目标前后站"]]
    trainInfoNeed.columns = ["车次", "到时", "开时", "检票口", "前后站"]
    # print(trainInfoNeed.head())

    return trainInfoNeed


def generateRoute(dataser: pandas.Series):

    s1 = "黄河南线路所"
    s2 = "大漠刘线路所"
    return None
#


def generateArriveLeave(datafr: pandas.DataFrame, mark=0) -> pandas.DataFrame:
    ALStDF = pandas.DataFrame(columns=['车站名称', '股道', '到达时间', '停站时间'])  # 进场信息

    ALStDF['车站名称'] = datafr["前后站"].apply(lambda x: x[mark])
    ALStDF['股道'] = ALStDF['车站名称'].apply(lambda x: station[x][2+mark])

    '''
    拟在该处依照股道插入线路所
    函数---- 拓扑排序 广度优先搜索BFS？或是单纯映射
    '''

    ALStDF['到达时间'] = datafr.apply(
        lambda x: arrLeaTime(x["到时"], x["前后站"], mark), axis=1)
    ALStDF['停站时间'] = 0

    return ALStDF


def generateMainSt(datafr: pandas.DataFrame):
    MainStDF = pandas.DataFrame(columns=['车站名称', '股道', '到达时间', '停站时间'])  # 进场信息

    # 计算停站时长，得到整形类型的时长，非浮点数没有.0便于写入文件
    MainStDF["停站时间"] = (datafr["开时"]-datafr["到时"]
                        ).apply(lambda x: stopStTime(x))
    # 计算并规整进场离场和停站时间，将三个到时改为游戏时分秒格式 hh:mm:ss
    MainStDF["到达时间"] = datafr["到时"].apply(lambda x: ModtimeStr(x))
    # 按照相应格式处理车站检票口为对应形式
    MainStDF["股道"] = datafr["检票口"].apply(lambda x: checkin(x))

    # 填充车站为中心车站
    MainStDF["车站名称"].fillna(value="济南西", inplace=True)
    return MainStDF


def generateTrainInfo(dataser: pandas.Series) -> pandas.Series:
    res = dataser.apply(lambda x: speMarType(x))
    # print(res.head())
    return res


def generateStr(fn: str):
    # 生成游戏样式的字符串
    f = open(file=fn, encoding="utf8", mode="w")
    for i in range(0, len(arriveStDF)):
        # format为对应顺序格式
        tf = "{train} : {arrive} {stop} {leave}".format(
            train=trainstr[i], arrive=arrivestr[i], stop=stopstr[i], leave=leavestr[i])
        print(tf)
        f.write(tf+"\n")

    f.close()
    return


at = processTrains("ltInfo.txt", "济南西")
print(at)

at.to_csv(path_or_buf="c2.txt", sep=",", encoding="utf8", index=False)


# 生成dataframe格式的数据
arriveStDF = generateArriveLeave(at, mark=0)
leaveStDF = generateArriveLeave(at, mark=1)
stopStDF = generateMainSt(at)
trainDF = generateTrainInfo(at["车次"])

# 按照四部分生成需求的字符格式，使用to_csv函数来生成
arrivestr = arriveStDF.to_csv(
    sep="#", header=False, index=False).split(sep="\r\n")
leavestr = leaveStDF.to_csv(sep="#", header=False,
                            index=False).split(sep="\r\n")
stopstr = stopStDF.to_csv(sep="#", header=False, index=False).split(sep="\r\n")
trainstr = trainDF.to_csv(header=False, index=False).split(sep="\r\n")

# generateStr("测试.txt")
=======

import pandas
import numpy
import datetime
import random
import networkx
desired_caps = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '9',  # 手机安卓版本
    'deviceName': 'xxx',  # 设备名，安卓手机可以随意填写

    'appPackage': 'tv.danmaku.bili',  # 启动APP Package名称
    'appActivity': '.MainActivityV2',  # 启动Activity名称

    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App
    'newCommandTimeout': 6000,
    'automationName': 'UiAutomator2'
    # 'app': r'd:\apk\bili.apk',
}
# {
#   "platformName": "Android",
#   "platformVersion": '9',
#   "deviceName": "xxx",
#   "appPackage": "",
#   "appActivity": ". ",
#   "unicodeKeyboard": True,
#   "reseteyboard": True,
#   "noReset": True,
#   "newCommandTimeout": 6000,
#   "automationName" :"UiAutomator2"
# }

# 读取文件，设置列名便于后续操作

species = {'新空调普快': ['120', 'LPPPPPP', 0], '新空调快速': ['120', 'LPPPPPP', 0],
           '新空调特快': ['140', 'LPPPPPP', 0], '新空调直快': ['160', 'LPPPPPP', 0],
           '动车': ['200', 'LPPL', 1], '城际': ['200', 'LPPL', 1], '高速': ['300', 'LPPLLPPL', 2]}
species1 = {'K': ['120', 'LPPPPPP', 0], 'T': ['140', 'LPPPPPP', 0], 'Z': ['160', 'LPPPPPP', 0],
            'D': ['200', 'LPPL', 1], 'C': ['200', 'LPPL', 1], 'G': ['300', 'LPPLLPPL', 2]}

# 车站-编号,掉向,用时以及运行车辆种类映射关系
# 图片左(0)右(1)侧线路key值相同则掉向,
# 国铁车辆行走左侧,2为数据为左侧股道编号
# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
station = {
    '京济联络线济南方向': ['b', 0, 2, 1, 8], '济郑高速长清方向': ['c', 0, 2, 1, 7],
    '济南西站': ['d', -1, 0, 0, 7], '济南西动车所': ['e', -1, 0, 0, 30],
    '京沪高速德州东方向': ['f', 1, '1', '2', 6, ], '京沪高速泰安站方向': ['a', 0, 2, 1, 7, ],
    '石济客专齐河方向': ['g', 1, 1, 2, 6], '石济客专济南东方向': ['h', 1, 1, 2, 6, ],
}

# orient="index", columns=["车站编号", "车站所在侧", "进场股道", "离场股道", "到达中心时间"]

# 线路和车站关系，主要用于从车站-值获取线路-键
route1 = {
    '济南西动车所': ["济南西"], '京济联络线济南方向': ["济南"], '济郑高速长清方向': ["长清"],
    '京沪高速泰安站方向': ["泰安", "曲阜东", "滕州东", "枣庄", "徐州东", "宿州东", "蚌埠南", "南京南"],
    '京沪高速德州东方向': ["北京南", "天津西", "天津", "沧州西", "德州东"],
    '石济客专齐河方向': ["齐河", "禹城东", "平原东"], '石济客专济南东方向': ["济南东"]}
# 两个合在一起写太难看




def dealTime(datafr: pandas.DataFrame) -> pandas.DataFrame:
    # 对于始发车和终到车进行时间处理，默认相同
    for idx, row in datafr.iterrows():
        if row["到时"] == "--:--":
            row["到时"] = row["开时"]
        elif row["开时"] == "--:--":
            row["开时"] = row["到时"]
    # 计算停站时间
    datafr["到时"] = pandas.to_datetime(datafr["到时"])
    datafr["开时"] = pandas.to_datetime(datafr["开时"])
    # 实发终到设置停站时间
    # pd["停站时间"].replace(0,10,inplace=True)

    return datafr


def stopStTime(stopTime: pandas.Timedelta) -> int:
    a = int(stopTime.seconds/60)  # 处理为数值类型的分钟时间
    # 始发或是终到的时间是随机的
    return a if a > 0 else random.randint(10, 30)


def ModtimeStr(switchTime: pandas.Timestamp) -> str:
    # 处理为仅有时分秒样式的字符串格式的时间
    return switchTime.strftime("%H:%M:%S")


def speMarType(traincode: str) -> str:  # 目前获取编组信息的方式
    til = species1[traincode[0]]  # 处理获取车辆信息字符串部分
    return "{cod} COMMUTER {speed} {mar} X1".format(cod=traincode, speed=til[0], mar=til[1])


def checkin(entrance: str) -> int:
    # 终到车
    res = 0
    if entrance == "无检票口信息":
        res = 0
    else:  # 检票口15A 非终到车
        res = int(entrance.strip("检票口AB"))
    return res


# 'D1636 COMMUTER 200 LPPL X1 : b#2#10:27:00#0 d#17#10:35:00#2 g#2#10:43:00#0 ',


def prevnextST(stopSt: list[str], stIdx: int) -> list[str]:
    # 返回结果，获取目标车站的前后车站
    res = ["", ""]
    res1 = ["", ""]
    if stIdx == 0:  # 始发车视为始发车站和下一站
        res = [stopSt[0], stopSt[1]]
    elif stIdx == len(stopSt)-1:  # 终到车视为前一站和终到站
        res = [stopSt[len(stopSt)-2], stopSt[len(stopSt)-1]]
    else:  # 中间站
        res = [stopSt[stIdx-1], stopSt[stIdx+1]]
    # 判断并修改进路
    for k, v in route1.items():
        if res[0] in v:
            res1[0] = k
        elif res[1] in v:
            res1[1] = k
    return res1


def arrLeaTime(t1: pandas.Timestamp, st: list[str], mark: int) -> str:
    tarst = st[mark]
    useTime = station[tarst][4]
    if mark == 0:  # 进场
        res = t1-datetime.timedelta(minutes=useTime)
    else:
        res = t1+datetime.timedelta(minutes=useTime)
    return res.strftime("%H:%M:%S")


'''
a={'G2664,蚌埠南,19:50到,19:54开,检票口检票口1,\n', 'G2664,济南西,21:39到,--:--开,无检票口信息,\n', 'G2664,合肥,18:50到,19:12开,无检票口信息,\n', 'G2664,六安,18:08到,18:10开,检票口二层检票口,\n', 'G2664,汉口,--:--到,16:48开,检票口二楼B6,\n', 'G2664,徐州东,20:31到,20:36开,检票口东广场进站7A7B检票,\n'}
f =open(file="ltInfo.txt", mode="w", encoding="utf-8")
for it in a:
    it=it.replace("到","").replace("开","")
    f.write(it)
f.close()

'''


def processTrains(fn: str, targetSt: str) -> pandas.DataFrame:
    # 处理产生初步所需信息的数据框
    trainsFrame = pandas.read_csv(filepath_or_buffer=fn,
                                  sep=",", encoding="utf8", header=None)
    trainsFrame.columns = ["车次",  "停站", "到时", "开时", "检票口", "drop1"]
    trainsFrame.drop(columns=["drop1"], inplace=True)

    trainsFrame = dealTime(trainsFrame)  # 初步处理时间
    trainsFrame.sort_values(by=["车次", "到时"], inplace=True)  # 归类排序
    # 整理为分钟样式的停站时间
    #trainsFrame["停站时间"] = trainsFrame["停站时间"].apply(lambda x: stopStTime(x))
    trainsFrame.reset_index(drop=True, inplace=True)
    # 按照车次分组为列表，同时车次不作为索引以便于操作
    tfgp = trainsFrame.groupby(by=["车次"], as_index=False).agg(list)
    # 获取目标停站的索引值，设置为一个辅助列
    tfgp["auxIdx"] = tfgp['停站'].apply(lambda x: x.index(targetSt))

    # 获取前后停站以得到更好的交路映射
    tfgp["目标前后站"] = tfgp.apply(
        lambda x: prevnextST(x["停站"], x["auxIdx"]), axis=1)
    # 获取其他信息
    tfgp["目标站到时"] = tfgp.apply(lambda x: x["到时"][x["auxIdx"]], axis=1)
    tfgp["目标站开时"] = tfgp.apply(lambda x: x["开时"][x["auxIdx"]], axis=1)
    tfgp["目标站检票口"] = tfgp.apply(lambda x: x["检票口"][x["auxIdx"]], axis=1)

    # 提取需要的信息为新的dataframe
    trainInfoNeed = tfgp[["车次", "目标站到时", "目标站开时", "目标站检票口", "目标前后站"]]
    trainInfoNeed.columns = ["车次", "到时", "开时", "检票口", "前后站"]
    # print(trainInfoNeed.head())

    return trainInfoNeed


def generateRoute(dataser: pandas.Series):

    s1 = "黄河南线路所"
    s2 = "大漠刘线路所"
    return None
#


def generateArriveLeave(datafr: pandas.DataFrame, mark=0) -> pandas.DataFrame:
    ALStDF = pandas.DataFrame(columns=['车站名称', '股道', '到达时间', '停站时间'])  # 进场信息

    ALStDF['车站名称'] = datafr["前后站"].apply(lambda x: x[mark])
    ALStDF['股道'] = ALStDF['车站名称'].apply(lambda x: station[x][2+mark])

    '''
    拟在该处依照股道插入线路所
    函数---- 拓扑排序 广度优先搜索BFS？或是单纯映射
    '''

    ALStDF['到达时间'] = datafr.apply(
        lambda x: arrLeaTime(x["到时"], x["前后站"], mark), axis=1)
    ALStDF['停站时间'] = 0

    return ALStDF


def generateMainSt(datafr: pandas.DataFrame):
    MainStDF = pandas.DataFrame(columns=['车站名称', '股道', '到达时间', '停站时间'])  # 进场信息

    # 计算停站时长，得到整形类型的时长，非浮点数没有.0便于写入文件
    MainStDF["停站时间"] = (datafr["开时"]-datafr["到时"]
                        ).apply(lambda x: stopStTime(x))
    # 计算并规整进场离场和停站时间，将三个到时改为游戏时分秒格式 hh:mm:ss
    MainStDF["到达时间"] = datafr["到时"].apply(lambda x: ModtimeStr(x))
    # 按照相应格式处理车站检票口为对应形式
    MainStDF["股道"] = datafr["检票口"].apply(lambda x: checkin(x))

    # 填充车站为中心车站
    MainStDF["车站名称"].fillna(value="济南西", inplace=True)
    return MainStDF


def generateTrainInfo(dataser: pandas.Series) -> pandas.Series:
    res = dataser.apply(lambda x: speMarType(x))
    # print(res.head())
    return res


def generateStr(fn: str):
    # 生成游戏样式的字符串
    f = open(file=fn, encoding="utf8", mode="w")
    for i in range(0, len(arriveStDF)):
        # format为对应顺序格式
        tf = "{train} : {arrive} {stop} {leave}".format(
            train=trainstr[i], arrive=arrivestr[i], stop=stopstr[i], leave=leavestr[i])
        print(tf)
        f.write(tf+"\n")

    f.close()
    return


at = processTrains("ltInfo.txt", "济南西")
print(at)

at.to_csv(path_or_buf="c2.txt", sep=",", encoding="utf8", index=False)


# 生成dataframe格式的数据
arriveStDF = generateArriveLeave(at, mark=0)
leaveStDF = generateArriveLeave(at, mark=1)
stopStDF = generateMainSt(at)
trainDF = generateTrainInfo(at["车次"])

# 按照四部分生成需求的字符格式，使用to_csv函数来生成
arrivestr = arriveStDF.to_csv(
    sep="#", header=False, index=False).split(sep="\r\n")
leavestr = leaveStDF.to_csv(sep="#", header=False,
                            index=False).split(sep="\r\n")
stopstr = stopStDF.to_csv(sep="#", header=False, index=False).split(sep="\r\n")
trainstr = trainDF.to_csv(header=False, index=False).split(sep="\r\n")

# generateStr("测试.txt")
>>>>>>> df47c64 (初始提交)

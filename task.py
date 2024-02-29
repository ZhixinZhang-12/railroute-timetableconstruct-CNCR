import uiautomation as auto
import subprocess
import datetime
import time
import itertools
import multiprocessing
from multiprocessing.queues import Queue
import numpy
import pandas
import random


# 速度和编组以及类型映射关系,0为普速1为动车2为高速，后续修改
species1 = {'K': ['120', 'LPPPPPPP', "0"], 'T': ['140', 'LPPPPPPP', "0"], 'Z': ['160', 'LPPPPPPP', "0"],
            'D': ['250', 'LLPPPPLL', "1"], 'C': ['200', 'LPPL', "1"], 'G': ['350', 'LPPLLPPL', "2"]}
species1default = ['120', 'LCPPPPPPP', "0"]
# 车站-编号,掉向,用时以及运行车辆种类映射关系
# 图片左(0)右(1)侧线路key值相同则掉向,
# 国铁车辆行走左侧,2为数据为左侧股道编号

# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
gameStationInfo = {'武汉站': ['a', -1, 0, 0, 0], '动车所': ['b', 0, 0, 0, 20],
                   '汉口': ['e', 0, 2, 1, 5],
                   '孝感北': ['d', 0, 1, 2, 4], '红安西': ['k', -1, 1, 2, 4],
                   '咸宁北': ['c', 0, 2, 1, 3],
                   '鄂州': ['f', -1, 2, 1, 5], '黄冈': ['g', 0, 2, 1, 5],
                   '葛店南站': ['葛店南', -1, 0, 0, 5],
                   }
gameStationDefault = ['未知', -1, 0, 0, 20]  # 找不到的默认设置

# 线路和车站关系，主要用于从车站-值获取线路-键
route1 = {'动车所': ["src", "dst"],
          '汉口': ["汉口"], '葛店南站': ["葛店南"],
          '红安西': ["红安西", "麻城北", "六安", "金寨", "合肥", "合肥南", "南京南"],
          '孝感北': ["孝感北", "信阳东", "明港东", "驻马店西", "漯河西", "许昌东", "郑州东", "郑州"],
          '咸宁北': ["咸宁北", "赤壁北", "岳阳东", "汨罗东", "长沙南", "广州南", "广州白云"],
          '鄂州': ["华容南", "鄂州", "黄石北", "大冶北", "白沙铺", "阳新", "瑞昌西", "庐山", "九江", "南昌西", "南昌"],
          '黄冈': ["华容东", "黄冈西", "黄冈东", "浠水南", "蕲春西", "武穴北", "黄梅东"],
          }
route1Default = ["src", "dst"]  # 找不到的默认设置


def mapEntrRoute(src, dst, arrtime, depatime):
    # a = 武汉站 | 1 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
    # b = 武汉动车所 | 1 | 1, 2, 3, 4
    # c = 京广高速咸宁北方向 | 1 | 1, 2
    # d = 京广高速孝感北方向 | 1 | 1, 2
    # e = 丹水池联络线汉口方向 | 1 | 1, 2
    # f = 武九客专鄂州方向 | 1 | 1, 2
    # g = 武岗城际黄冈东方向 | 1 | 1, 2
    # h = 葛店南站 | 1 | 1, 2, 3, 4
    # j = 滠口线路所 | 1 | 1, 2
    # k = 沪蓉线红安西方向 | 1 | 1, 2
    # n = 湛家矶线路所 | 1 | 1, 2
    # p = 武汉南线路所 | 1 | 1, 2, 3, 4
    stgp1 = "fgh"  # 武九客专方向
    stgp2 = "c"  # 咸宁北
    stgp3 = "dk"  # 京广高速郑州、沪蓉线合肥方向
    stgp4 = "e"  # 汉口
    arrLinePost = ""
    depaLinePost = ""
    entret = 0
    if src == "b":
        entret = random.randint(1, 15)

    elif src == "e" and dst == "c":
        entret = random.randint(7, 15)
        arrLinePost = "j#1#{t}#0 ".format(t=arrtime)
    elif src == "e" and dst in stgp1:
        entret = random.randint(16, 20)
        arrLinePost = "j#2#{t}#0 ".format(t=arrtime)
        depaLinePost = "p#1#{t}#0 ".format(t=depatime)
    elif src in stgp3 and dst == "c":
        entret = random.randint(7, 15)
    elif src in stgp3 and dst in stgp1:
        entret = random.randint(7, 15)
        arrLinePost = "p#3#{t}#0 ".format(t=arrtime)

    elif src == "c" and dst == "e":
        entret = random.randint(1, 8)
        depaLinePost = "n#2#{t}#0 ".format(t=depatime)
    elif src == "c" and dst in stgp3:
        entret = random.randint(1, 8)
    elif src in stgp1 and dst == "e":
        entret = random.randint(16, 20)
        arrLinePost = "p#3#{t}#0 ".format(t=arrtime)
        depaLinePost = "n#2#{t}#0 ".format(t=depatime)
    elif src in stgp1 and dst in stgp3:
        entret = random.randint(1, 8)
        arrLinePost = "p#1#{t}#0 ".format(t=arrtime)

    else:  # 客机始发
        entret = 0

    return [arrLinePost, entret, depaLinePost]


class lltskbProcess(object):
    def __init__(self, lltskbroute: str, traincount: int):  # 构造函数，调整设置和日志记录并启动程序

        auto.uiautomation.SetGlobalSearchTimeout(10)
        # set it to False and try again, default is False
        auto.uiautomation.DEBUG_EXIST_DISAPPEAR = True
        # set it to False and try again, default is False
        auto.uiautomation.DEBUG_SEARCH_TIME = True
        subprocess.Popen(
            "start {route}".format(route=lltskbroute), shell=True)
        self.window = auto.WindowControl(searchDepth=1, ClassName='#32770')
        self.window.SetActive()  # 打开程序并激活窗口
        self.rowcount = 18
        self.pagecount = int(traincount/18)+1
        return

    def initsetting(self, querytype=1):  # 对于车型选择（未加入），模糊车站等选择
        # 1为始发站，2为终到站，3为车站查询输入的车站，foundindex不从0开始
        # if querytype==1:
        self.stationquery = self.window.EditControl(
            searchDepth=2, foundIndex=3, AutomationId="1001")
        self.stationquery.Click()  # 点击以激活输入框

        # 返回值为0为未选中，返回值1为选中
        isoperate = auto.CheckBoxControl(
            searchDepth=2, AutomationId="1024")  # 当日不开行
        if isoperate.GetTogglePattern().ToggleState == 1:
            isoperate.Click()  # 勾选以隐藏未开行车次

        # 返回值为0为未选中，返回值1为选中
        isobscure = auto.CheckBoxControl(
            searchDepth=2, AutomationId="1025")  # 模糊车站
        if isobscure.GetTogglePattern().ToggleState == 1:
            isobscure.Click()  # 取消勾选以获得准确单个车站

        return

    def selectstation(self, station: str):  # 按照车站查询

        self.stationquery.Click()  # 点击以激活输入框
        self.stationquery.SendKeys('{Ctrl}a{Del}', waitTime=0.1)  # 全选清空内容
        self.stationquery.SendKeys(text=station, waitTime=0.1)  # 输入需要查询的车站名称

        self.quetybtn = self.window.ButtonControl(
            searchDepth=1, foundIndex=1, AutomationId="1006")  # 查询按钮
        self.quetybtn.Click(waitTime=0.1)  # 点击查询按钮

        return

    def selecttrain(self, train: str):  # 按照单个车次查询部分，和上面几乎一致

        return

    def generateroute(self, InfoQueueProd, trainCodeQueueProd):

        list1 = self.window.PaneControl(searchDepth=1, foundIndex=1,
                                        AutomationId="1019")  # 获取PaneControl控件，一级页面
        list1.Click(waitTime=0.1)  # 第一次点击激活首页的表格，但是同时会激活单一车次二级页面并聚焦
        list2 = self.window.PaneControl(searchDepth=2, foundIndex=1,
                                        AutomationId="1019")  # 获取PaneControl控件，一级页面
        list1.Click(x=20, y=30, waitTime=0.1)  # 第二次继续点击首页表格重新激活一级表格并选中第一行
        pgdnbtn = auto.ButtonControl(searchDepth=4,
                                     AutomationId="DownPageButton")  # 翻页按钮
        # for i, j in itertools.product(range(0, pagecount), range(0, rowcount)):
        for j in range(0, self.pagecount):  # 翻页
            for i in range(0, self.rowcount):  # 一页
                # 每一次激活新的二级页面y值向下移动25左右
                list1.Click(x=20, y=30+23*i, waitTime=0.1)

                list2.Click(waitTime=0.1)  # 激活二级页面
                list2.SendKeys('{Ctrl}a{Ctrl}c', waitTime=0.1)  # 全选并复制内容
                result = auto.GetClipboardText()  # 复制到剪切板
                InfoQueueProd.put(result, timeout=1)  # 加入队列
                traincode = list2.GetParentControl().Name
                trainCodeQueueProd.put(traincode, timeout=1)  # 将列车号即二级页面标题
            try:
                pgdnbtn.Click()  # 下一页按钮，大小会改变，应该需要重新选择?到底了多点两次似乎也不算报错
            except LookupError as le:
                print(le)
                break
        return

    def __del__(self,):  # 析构函数，记录日志关闭窗口
        auto.Logger.Write('Data acquisition completed.\n',
                          auto.ConsoleColor.Cyan)
        self.window.Disappears(1)  # 确认窗口状态并关闭
        self.window.GetWindowPattern().Close()
        self.window.Exists(1)  # 记录日志

        return


def obtaintrain(lltroute: str, tc: int, tarstation: str, InfoQueue: Queue, trainCodeQueue: Queue):
    # 生产者进程函数
    lltpro = lltskbProcess(
        lltskbroute=lltroute, traincount=tc)
    lltpro.initsetting()  # 处理获取时刻表信息
    lltpro.selectstation(station=tarstation)
    lltpro.generateroute(InfoQueue, trainCodeQueue)

    return


def initStrFormate(station: str, initcodeStr: str, initInfoStr: str):
    # 使用最初得到的字符数据
    traincodeStr = initcodeStr.replace("次", "")  # 字符串样式车次便于最后生成游戏样式的字符串
    if "B" in traincodeStr:
        traincodeStr = traincodeStr.replace("B", "")
    traincodeList = traincodeStr.split(sep="/")  # 列表样式便于下面处理
    if len(traincodeList) == 2:  # 如果变化车次，使用0号位车次替代便于一起处理
        initInfoStr = initInfoStr.replace(
            traincodeList[1], traincodeList[0])  # [1:]

    # 按照车次数字部分分割，因为复制过来车次有首位缺失
    initList = initInfoStr.split(traincodeList[0])
    tarposi = 0
    for i, e in enumerate(initList):
        if station+"\t" in e:  # 目标车站
            tarposi = i  # 获取目标车站位置，暂不考虑环线停靠两次等
            break
    prepareList = [[], [], []]  # 长度为3的空列表
    if tarposi == 1:  # 始发车,0位元素为可能剩下的列车类型字母cdg等
        prepareList = [[traincodeStr, "src", "00:00", "00:00", "0", "0"],
                       (traincodeStr + initList[1]
                        ).split(sep="\t", maxsplit=6),
                       (traincodeStr+initList[2]).split(sep="\t", maxsplit=6)]
    elif tarposi == len(initList)-1:  # 终到车
        prepareList = [(traincodeStr+initList[tarposi-1]).split(sep="\t", maxsplit=6),
                       (traincodeStr + initList[tarposi]
                        ).split(sep="\t", maxsplit=6),
                       [traincodeStr, "dst", "23:59", "23:59", "9999", "0"]]
    else:  # 过路车
        prepareList = [(traincodeStr+initList[tarposi-1]).split(sep="\t", maxsplit=6),
                       (traincodeStr + initList[tarposi]
                        ).split(sep="\t", maxsplit=6),
                       (traincodeStr+initList[tarposi+1]).split(sep="\t", maxsplit=6)]

    for i in range(3):
        while len(prepareList[i]) <= 6:  # 如果最后一列缺失
            prepareList[i].append("0")
        while len(prepareList[i]) > 6:  # 超长的截取
            prepareList[i].pop()
        if prepareList[i][2] == "-- --":  # 替换中心车站时间从-- --到到达时间
            prepareList[i][2] = prepareList[i][3]
        elif prepareList[i][3] == "-- --":  # 替换进场车站离开时间
            prepareList[i][3] = prepareList[i][2]

    return prepareList


def routeStrFormate(prepareList: list[list]):
    # 使用上面初步处理的数据帧并完成进一步处理
    # print(prepareList)
    traindf = pandas.DataFrame(data=prepareList, index=None, columns=[
        "traincode", "station", "arrival", "departure", "totalmiles", "entrance"])
    traindf["arrival"] = pandas.to_datetime(
        arg=traindf["arrival"],  format="%H:%M")
    traindf["departure"] = pandas.to_datetime(
        arg=traindf["departure"],  format="%H:%M")
    traindf["stoptime"] = (traindf["departure"] -
                           traindf["arrival"]).dt.total_seconds() / 60
    traindf["stoptime"] = traindf["stoptime"].apply(lambda x: int(x))

    # print(traindf)
    traingpdf = traindf.groupby(
        by="traincode", as_index=False, sort=False).agg(list)

    # dataframe--series--list,三级索引，0和2为前后站索引
    try:
        for k, v in route1.items():
            # 把车站名映射为线路，前后站一定不同所以可以循环判断两次
            if traingpdf["station"][0][0] in v:
                traingpdf["station"][0][0] = k
            elif traingpdf["station"][0][2] in v:
                traingpdf["station"][0][2] = k
    except IndexError:
        print(traingpdf["traincode"], "出现异常")
        traingpdf["station"][0][0] = traingpdf["station"][0][1]
        traingpdf["station"][0][2] = traingpdf["station"][0][1]

    # arriveroute = traingpdf["station"][0][0]
    # leaveroute = traingpdf["station"][0][2]
    # 计算理论进场离场时间
    traingpdf["arrival"][0][0] = traingpdf["arrival"][0][1] - \
        datetime.timedelta(
            minutes=(gameStationInfo.get(traingpdf["station"][0][0], gameStationDefault))[4])
    traingpdf["departure"][0][2] = traingpdf["departure"][0][1] + \
        datetime.timedelta(
            minutes=(gameStationInfo.get(traingpdf["station"][0][2], gameStationDefault))[4])

    return traingpdf
#


def generateGameStr(infodf: pandas.DataFrame, entRule=[]):
    # 最后生成游戏字符串，entrule为股道/检票口在entrance部分的位置范围
    # D5769/D5772 COMMUTER 200 LPPL X1 : 余花联络线南湖东方向#1#19:28:00#0 武汉东#2#19:34:00#5 余花联络线花山南方向###0
    trcode = infodf["traincode"][0]
    trtype = trcode[0]
    timfo = species1.get(trtype, ['120', 'LCPPPPPP', "0"])
    trainStr = "{tc} COMMUTER {spe} {mar} X1 : ".format(
        tc=trcode, spe=timfo[0], mar=timfo[1])
    ast = infodf["station"][0][0]  # 进场部分
    astref = gameStationInfo.get(ast, gameStationDefault)
    arrStr = "{sta}#{rail}#{clck}#{stay} ".format(
        sta=astref[0], rail=astref[2], clck=infodf["arrival"][0][0], stay=0)
    dst = infodf["station"][0][2]  # 离场部分
    dstref = gameStationInfo.get(dst, gameStationDefault)
    depStr = "{sta}#{rail}#{clck}#{stay} ".format(
        sta=dstref[0], rail=dstref[3], clck=infodf["departure"][0][2], stay=0)

    cst = infodf["station"][0][1]  # 停站部分

    erl = mapEntrRoute(src=astref[0], dst=dstref[0], arrtime=infodf["arrival"]
                       [0][0], depatime=infodf["departure"][0][2])
    sta1 = infodf["stoptime"][0][1]

    centerStr = "{sta}#{rail}#{clck}#{stay} ".format(
        sta="a", rail=erl[1], clck=infodf["arrival"][0][1], stay=sta1 if sta1 != 0 else 1)

    res = (trainStr+arrStr+erl[0]+centerStr +
           erl[2]+depStr).replace("1900-01-01 ", "")
    return res


def gameStrProcess(station, InfoQueueCons: Queue, trainCodeQueueCons: Queue, outfile: str):
    # 消费者函数
    resset = set()
    while True:
        if InfoQueueCons.empty() == True:
            print("队列已为空，暂时无元素可初步处理，消费者暂停5s")
            time.sleep(5)
            continue
        initInfo = InfoQueueCons.get(timeout=1)
        if initInfo == "114514":
            break
        initcode = trainCodeQueueCons.get(timeout=1)

        initpr1 = initStrFormate(
            station=station, initcodeStr=initcode, initInfoStr=initInfo)
        nextpr2 = routeStrFormate(prepareList=initpr1)
        outstr = generateGameStr(nextpr2, [0, 0])
        resset.add(outstr)
    print(resset)
    f = open(file=outfile, mode="w", encoding="utf-8")
    for rs in resset:
        f.write(rs+"\n")
        print(rs)
    f.close()
    return


def strReproduct(file1: str, file2: str):
    codelist = []
    infolist = []
    with open(file=file1, mode="r", encoding="utf-8") as f:
        for li in f:
            info1 = li
            code1 = li.split(sep=" ", maxsplit=1)[0]
            if code1 not in codelist:
                codelist.append(code1)
                infolist.append(info1)
            else:
                continue
    f.close()
    infolist.sort()
    with open(file=file2, mode="w", encoding="utf-8") as w:
        for i in infolist:
            w.writelines(i)
    w.close()

    return


if __name__ == "__main__":
    InfoQueue1 = multiprocessing.Queue()  # 径路信息队列
    trainCodeQueue1 = multiprocessing.Queue()  # 车次号队列
    # 中继承接队列
    targetstation = "武汉"

    lltskbroute = "C:\\Users\\zzhix\\Downloads\\lltskb\\lltskb.exe"

    p = multiprocessing.Process(
        target=obtaintrain, args=(lltskbroute, 550, targetstation, InfoQueue1, trainCodeQueue1,))
    c = multiprocessing.Process(
        target=gameStrProcess, args=(targetstation, InfoQueue1, trainCodeQueue1, "text2.txt"))

    p.start()  # 启动生产者和消费者进程
    time.sleep(10)  # 启动较慢，等待生产者初始化完成
    c.start()

    p.join()  # 等待生产者进程完成
    InfoQueue1.put("114514")  # magic number,通知消费者所有产品已经生产完毕
    c.join()  # 等待消费者进程完成

    pass

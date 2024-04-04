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
import requests

'''
# a = 宜昌东站 | 1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 
# b = 宜昌东客整所,动车所 | 1 | 1, 2 
# c = 沪蓉线恩施方向 | 1 | 1, 2  野三关 高坪 建施 恩施 利川 石柱县 丰都 长寿北 重庆北
# d = 沪蓉线荆州方向 | 1 | 1, 2  枝江北 荆州 潜江 天门南 仙桃西 汉川 汉口 武昌
# e = 焦柳线松滋方向 | 1 | 1, 2 枝城 松滋 张家界 石门县北
# f = 焦柳线荆门方向 | 1 | 1, 2 荆门 宜城 襄阳
# g = 鸦雀岭 | 1 | 1, 2, 3, 4, 5 
# h = 鸦宜线宜昌方向 | 1 | 1 宜昌
# i = 沪渝蓉高速铁路恩施南方向(在建) | 1 | 1, 2 
# j = 沪渝蓉高速铁路宜昌北方向(在建) | 1 | 1, 2 
# k = 宜昌西线路所 | 1 | 2, 1, 3, 4 
# l = 宜昌东线路所 | 1 | 1, 2, 3, 4 
# m = 宜昌东疏解线 | 1 | 1, 2 
# n = 宜昌长江特大桥 | 1 |  
# o = 宜昌东一场 | 1 | 1, 2, 3 
# p = 新昌 | 1 | 1, 2, 3 
 
905|905 COMMUTER 120 LPPPL X1 : c#1#08:00:00#0 k#2#08:03:00#0 a#6#08:06:00#0 l#2#08:10:00#0 d#1#08:14:00#0
535|535 COMMUTER 120 LPPPL X1 : e#0#08:00:00#0 a#0#08:15:00#3 c#0#08:24:00#0
846|846 COMMUTER 120 LPPPL X1 : f#0#08:00:00#0 a#0#08:15:00#1 c#2#08:22:00#0
623|623 COMMUTER 120 LPPPL X1 : e#2#08:00:00#0 f#0#08:05:00#0
878|878 COMMUTER 120 LPPPL X1 : b#0#00:00:00#0 a#8#00:04:00#0 c#0#00:09:00#0
831|831 COMMUTER 120 LPPPL X1 : c#1#08:00:00#0 a#0#08:06:00#6 d#1#08:18:00#0
URBAN
'''

# 速度和编组以及类型映射关系,0为普速1为动车2为高速，后续修改
species1 = {'K': ['120', 'LCPPPPPP', "0"], 'T': ['140', 'LCPPPPPP', "0"], 'Z': ['160', 'LCPPPPPP', "0"],
            'D': ['250', 'LLPLPPLL', "1"], 'C': ['200', 'LPPL', "1"], 'G': ['350', 'LPLPPLPL', "2"]}
species1default = ['120', 'LCPPPPPPP', "0"]
# 游戏里放16编组的实在是太长了，所以目前还是不准备使用对应编组爬取部分
marshalling = {"": ""}

# d = 焦柳线松滋方向 | 1 | 1, 2 枝城 松滋 张家界 石门县北
# f = 焦柳线荆门方向
# 车站-编号,进场立场股道,用时
# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
# 对于股道，若为边界进出场车站股道为进场立场行走股道编号，若为越行站则为对应正线、越行线编号
gameStationInfo = {'宜昌东': ['a', 0, 0, 0], '宜昌东客整所,动车所': ['b', 0, 0, 20],
                   '沪蓉线恩施方向': ['c', 1, 2, 10], '沪蓉线荆州方向': ['d', 2, 1, 10],
                   '焦柳线松滋方向': ['e', 2, 1, 15], '焦柳线荆门方向': ['f', 1, 2, 15],
                   '鸦雀岭': ['g', 2, 1, 10], '新昌': ['p', 1, 1, 6],
                   '宜昌西线路所': ['k', 2, 1, 5], '宜昌东线路所': ['l', 2, 1, 5],
                   }
gameStationDefault = ['b',  0, 0, 20]  # 找不到的默认设置

# 线路和车站关系，主要用于从车站-值获取线路-键
route12 = {
    "野三关": ["沪蓉线恩施方向", "宜昌西线路所"], "高坪": ["沪蓉线恩施方向", "宜昌西线路所"],
    "建始": ["沪蓉线恩施方向", "宜昌西线路所"], "恩施": ["沪蓉线恩施方向", "宜昌西线路所"], "利川": ["沪蓉线恩施方向", "宜昌西线路所"],
    "石柱县": ["沪蓉线恩施方向", "宜昌西线路所"], "丰都": ["沪蓉线恩施方向", "宜昌西线路所"],
    "长寿北": ["沪蓉线恩施方向", "宜昌西线路所"], "重庆北": ["沪蓉线恩施方向", "宜昌西线路所"],

    "枝江北": ["沪蓉线荆州方向", "宜昌东线路所"], "荆州": ["沪蓉线荆州方向", "宜昌东线路所"],
    "潜江": ["沪蓉线荆州方向", "宜昌东线路所"], "天门南": ["沪蓉线荆州方向", "宜昌东线路所"], "仙桃西": ["沪蓉线荆州方向", "宜昌东线路所"],
    "汉川": ["沪蓉线荆州方向", "宜昌东线路所"], "汉口": ["沪蓉线荆州方向", "宜昌东线路所"], "武昌": ["沪蓉线荆州方向", "宜昌东线路所"],

    "枝城": ["焦柳线松滋方向", "新昌"], "松滋": ["焦柳线松滋方向", "新昌"],
    "张家界": ["焦柳线松滋方向", "新昌"], "石门县北": ["焦柳线松滋方向", "新昌"],

    "荆门": ["焦柳线荆门方向", "鸦雀岭", "新昌"], "宜城": ["焦柳线荆门方向", "鸦雀岭", "新昌"], "襄阳": ["焦柳线荆门方向", "鸦雀岭", "新昌"],

    "宜昌东客整所,动车所": ["宜昌东"],
}
route1Default = ["宜昌东客整所,动车所"]  # 找不到的默认设置

# 综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entrance12 = {
    ("沪蓉线恩施方向", "宜昌西线路所", "宜昌东", "宜昌东线路所", "沪蓉线荆州方向"): [1, 2, (5, 9), 2, 1],
    ("沪蓉线荆州方向", "宜昌东线路所", "宜昌东", "宜昌西线路所", "沪蓉线恩施方向"): [2, 3, (5, 9), 3, 2],

    ("沪蓉线恩施方向", "宜昌西线路所", "宜昌东", "新昌", "鸦雀岭", "焦柳线荆门方向"): [1, 2, (6, 9), 1, 4, 2],
    ("焦柳线荆门方向", "鸦雀岭", "新昌", "宜昌东", "沪蓉线恩施方向", "宜昌西线路所"): [1, 4, 1, (2, 5), 3, 2],

    ("宜昌东客整所,动车所", "宜昌东", "宜昌东线路所", "沪蓉线荆州方向"): [1, (6, 9), 2, 1],
    ("宜昌东客整所,动车所", "宜昌东", "宜昌西线路所", "沪蓉线恩施方向"): [2, (1, 5), 3, 2],

    ('宜昌东客整所,动车所', '宜昌东', '新昌', '鸦雀岭', '焦柳线荆门方向'): [1, (6, 9), 1, 4, 2],
    ('宜昌东客整所,动车所', '宜昌东', '新昌',  '焦柳线松滋方向'): [1, (6, 9), 1,  1],

    ('沪蓉线荆州方向', '宜昌东线路所', '宜昌东', '宜昌东客整所,动车所'): [2, 3, (1, 5), 2],
    ('沪蓉线恩施方向', '宜昌西线路所', '宜昌东', '宜昌东客整所,动车所'): [1, 2, (6, 9), 1],

}
entrance1Default = (0, 0, 0, 0, 0, 0)


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


def mapArrLeaTime(t1: pandas.Timestamp, st: str, mark: int) -> str:
    # 选取是进场还是立场
    useTime = gameStationInfo.get(st, gameStationDefault)[3]
    if mark == 0:  # 进场减时间
        res = t1-datetime.timedelta(minutes=useTime)
    else:  # 离场加时间
        res = t1+datetime.timedelta(minutes=useTime)
    # 返回时分秒格式的字符串
    return res.strftime("%H:%M:%S")


def mapEntrance0(st: str, way: int) -> int:
    routeEntrance = gameStationInfo.get(st, gameStationDefault)
    ent = 0
    if way == 0:  # 进场股道映射
        ent = routeEntrance[1]
    elif way == 1:  # 停站股道映射，最后会使用其他函数
        ent = 0
    else:  # 离场股道映射
        ent = routeEntrance[2]
    return ent


def mapEntrance1(df: pandas.DataFrame) -> list:
    # 改为元组来作为key查找
    routekey = tuple(df["station"].to_list())
    waykey = df["way"].to_list()
    entranceList = []
    try:  # 映射径路
        routelist = entrance12[routekey]
    except Exception:
        print("径路{r}未收录".format(r=routekey))
        entranceList = [0]*len(waykey)
    else:
        for i in range(0, len(waykey)):
            if waykey[i] == 1:  # 停站部分使用随机数
                entranceList.append(random.randint(
                    routelist[i][0], routelist[i][1]))
            else:  # 其他的则直接加入
                entranceList.append(routelist[i])

    return entranceList


def mapStationCode(st: str, traincode: str) -> str:
    stationCode = []
    try:
        stationInfo = gameStationInfo[st]
    except KeyError:
        print("{a}车次{b}车站未收录".format(a=traincode, b=st))
        stationCode = gameStationDefault[0]
    else:
        stationCode = stationInfo[0]  # type: ignore

    return stationCode


def routeStrFormate(prepareList: list[list]):
    # 使用上面初步处理的数据帧并完成进一步处理
    fullRoute2 = []
    centreStIdx = 0
    censt = prepareList[1]  # 中心车站位置
    for idx, ele in enumerate(prepareList):
        if idx == 0:  # 进场数据映射,进场时间均设置为到站时间
            routemap = route12.get(ele[1], route1Default)
            routeLi = [[ele[0], a, censt[2], censt[2], ele[5], 0]
                       for a in routemap]
            centreStIdx = len(routeLi)  # 记录中心车站顺序
        elif idx == 1:  # 停站数据直接合并加入
            routeLi = [[ele[0], ele[1], ele[2], ele[3], ele[5], 1]]
        else:  # 立场路线映射，离场时间均设置为发车时间
            routemap = route12.get(ele[1], route1Default)[::-1]  # 离场需要反转顺序
            routeLi = [[ele[0], a, censt[3], censt[3], ele[5], 2]
                       for a in routemap]
        fullRoute2 += routeLi  # 整理合并加入
    # 规整时间格式，改为时间戳以完成计算

    traindf = pandas.DataFrame(data=fullRoute2, index=None, columns=[
        "traincode", "station", "arrival", "departure", "entrance", "way"])

    traindf["arrival"] = pandas.to_datetime(
        arg=traindf["arrival"],  format="%H:%M")
    traindf["departure"] = pandas.to_datetime(
        arg=traindf["departure"],  format="%H:%M")
    # 计算停站时间，并将浮点数改为分钟整数
    traindf["stoptime"] = (traindf["departure"] -
                           traindf["arrival"]).dt.total_seconds() / 60
    traindf["stoptime"] = traindf["stoptime"].apply(lambda x: int(x))

    # 映射对应进场立场时间，同时转换为字符串
    traindf["arrival"] = traindf.apply(lambda x: mapArrLeaTime(
        t1=traindf.iloc[centreStIdx, 2], st=x["station"], mark=0), axis=1)  # type: ignore
    traindf["departure"] = traindf.apply(lambda x: mapArrLeaTime(
        t1=traindf.iloc[centreStIdx, 3], st=x["station"], mark=1), axis=1)  # type: ignore
    # 对于非中心车站进行映射
    # traindf["entrance"] = traindf.apply(
    #     lambda x: mapEntrance0(st=x["station"], way=x["way"]), axis=1)
    traindf["entrance"] = mapEntrance1(traindf)
    # 映射车站为对应字母编号

    traindf["station"] = traindf.apply(
        lambda x: mapStationCode(x["station"], x["traincode"]), axis=1)

    # traingpdf = traindf.groupby(
    #     by="traincode", as_index=False, sort=False).agg(list)
    # dataframe--series--list,三级索引，

    return traindf
#


def generateGameStr(infodf: pandas.DataFrame):
    # 最后生成游戏字符串，entrule为股道/检票口在entrance部分的位置范围
    # D5769/D5772 COMMUTER 200 LPPL X1 : 余花联络线南湖东方向#1#19:28:00#0 武汉东#2#19:34:00#5 余花联络线花山南方向###0
    trcode = infodf["traincode"][0]
    trtype = trcode[0]

    typeInfo = species1.get(trtype, species1default)
    trainStr = "{tc} COMMUTER {spe} {mar} X1 :".format(
        tc=trcode, spe=typeInfo[0], mar=typeInfo[1])
    routeStrList = [trainStr]
    for row in infodf.itertuples(index=False):
        if row.way == 0:
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=row.entrance, clck=row.arrival, stay=row.stoptime)
        elif row.way == 1:
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=random.randint(0, 7), clck=row.arrival, stay=row.stoptime)
        else:
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=row.entrance, clck=row.departure, stay=row.stoptime)
        routeStrList.append(routeStr)

    ret = " ".join(routeStrList)
    print(ret)
    return ret


def gameStrProcess(station, InfoQueueCons: Queue, trainCodeQueueCons: Queue, outfile: str):
    # 消费者函数
    resset = set()
    while True:
        if InfoQueueCons.empty() == True:
            print("队列已为空，暂时无元素可初步处理，消费者暂停5s")
            time.sleep(5)  # sleep一段时间来等待生产者并减少cpu占用
            continue
        initInfo = InfoQueueCons.get(timeout=1)
        if initInfo == "114514":
            break  # 发送magic number来停止
        initcode = trainCodeQueueCons.get(timeout=1)
        # 处理部分
        initpr1 = initStrFormate(
            station=station, initcodeStr=initcode, initInfoStr=initInfo)
        nextpr2 = routeStrFormate(prepareList=initpr1)
        outstr = generateGameStr(nextpr2)
        resset.add(outstr)  # 加入最后文件

    f = open(file=outfile, mode="w", encoding="utf-8")
    for rs in resset:  # 写入文件
        f.write(rs+"\n")
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
    targetstation = "宜昌东"

    # lltskbroute = "lltskb\\lltskb.exe"
    # strtest = "D5801	汉口	-- --	08:00	0	D5801	荆州	09:13	09:15	204	D5801	宜昌东	09:49	-- --	292"
    # initpr1 = initStrFormate(
    #     station=targetstation, initcodeStr="D5801", initInfoStr=strtest)
    # nextpr2 = routeStrFormate(prepareList=initpr1)
    # outstr = generateGameStr(nextpr2)
    # p = multiprocessing.Process(
    #     target=obtaintrain, args=(lltskbroute, 210, targetstation, InfoQueue1, trainCodeQueue1,))
    # c = multiprocessing.Process(
    #     target=gameStrProcess, args=(targetstation, InfoQueue1, trainCodeQueue1, "text2.txt"))

    # p.start()  # 启动生产者和消费者进程
    # time.sleep(10)  # 启动较慢，等待生产者初始化完成
    # c.start()

    # p.join()  # 等待生产者进程完成
    # InfoQueue1.put("114514")  # magic number,通知消费者所有产品已经生产完毕
    # c.join()  # 等待消费者进程完成
    strReproduct("宜昌东.txt", "宜昌东1.txt")

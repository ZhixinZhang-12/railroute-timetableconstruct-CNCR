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

# 速度和编组以及类型映射关系,0为普速1为动车2为高速，后续修改
lltskbroute = "lltskb\\lltskb.exe"

species1 = {'K': ['120', 'LCPPPPPPPP', "0"], 'T': ['140', 'LCPPPPPPPP', "0"], 'Z': ['160', 'LCPPPPPPPP', "0"],
            'D': ['250', 'LPPLLPPL', "1"], 'C': ['200', 'LPPL', "1"], 'G': ['350', 'LPLPPLPL', "2"]}
species1default = ['120', 'LCPPPPPPPP', "0"]
# 游戏里放16编组的实在是太长了，所以目前还是不准备使用对应编组爬取部分
marshalling = {"": ""}

# a = 襄阳东 | 1 | 18, 15, 16, 9, 10, 6, 3, 1, 20, 2, 7, 8, 11, 14, 17, 19
# b = 谷城北 | 1 | 1, 2
# c = 枣阳 | 1 | 5, 1, 6, 2, 3, 4
# d = 郑渝高速南阳东郑州东方向 | 1 | 1, 2
# e = 郑渝高速神农架重庆北方向 | 1 | 1, 2
# f = 襄阳东动车所 | 1 | 1, 2, 3
# g = 襄荆高速荆门东荆州方向(计划2025年完成) | 1 | 2, 1
# h = 东津线路所 | 1 |
# i = 随县 | 1 | 1, 2
# j = 随州南 | 1 | 1, 2, 3, 4
# k = 安陆西 | 1 | 1, 2
# l = 云梦东 | 1 | 3, 4, 1, 2
# m = 孝感东 | 1 | 3, 4, 1, 2
# n = 天河机场 | 1 | 1, 2, 3, 4
# o = 汉十高速/汉孝城际汉口方向 | 1 | 2, 1
# p = 丹江口 | 1 | 1, 2, 3
# q = 武当山西 | 1 | 1, 2
# r = 十堰东 | 1 | 1, 2, 3, 4, 5
# s = 武西高速西安东方向(计划2024年完成) | 1 | 1, 2
# t = 武汉枢纽直通线新汉阳方向(预留) | 1 | 1, 2

# 车站-编号,进场立场股道,用时
# [车站编号,车辆进场、上行股道,车辆离场、下行行走股道,到达中心车站所用时间]
# 对于股道，若为边界进出场车站股道为进场立场行走股道编号，若为纯越行站则为对应正线、越行线编号
# 线路所则为正线通过
gameStationInfo = {'襄阳东': ['a', (6, 9), (1, 3), 0],
                   '谷城北': ['b', (1, 1), (2, 2), 0],
                   '枣阳': ['c', (6, 6), (4, 5), 0],
                   '襄阳东动车所': ['f', (0, 0), (0, 0), 20],
                   '随县': ['i', (1, 1), (2, 2), 0],
                   '随州南': ['j', (3, 4), (1, 2), 0],
                   '安陆西': ['k', (2, 2), (1, 1), 0],
                   '云梦东': ['l', (1, 2), (3, 4), 0],
                   '孝感东': ['m', (3, 4), (1, 2), 0],
                   '天河机场': ['n', (1, 2), (3, 4), 0],
                   '丹江口': ['p', (1, 2), (3, 3), 0],
                   '武当山西': ['q', (1, 1), (2, 2), 0],
                   '十堰东': ['r', (1, 3), (4, 5), 10],
                   '汉口': ['o', (1, 1), (2, 2), 2],
                   '东津线路所': ['h', (3, 3), (4, 4), 0],

                   "巴东": ['e', (2, 2), (1, 1), 60],
                   "重庆北": ['e', (2, 2), (1, 1), 180],
                   "西安东": ['s', (2, 2), (1, 1), 10],

                   "郑州东": ['d', (1, 1), (2, 2), 100]
                   }
gameStationDefault = ['f',  0, 0, 20]  # 找不到的默认设置
# g = 襄荆高速荆门东荆州方向(在建) | 1 | 1, 2

# 提取出车站部分以减少打字量
hrHankou = ["汉口"]
jgWuhan = ["武汉"]
hrhefei = ["合肥南"]
hwdetourhefei = ["合肥"]
sectionList0 = ["汉口", "汉川", "天门南", "仙桃西", "潜江", "荆州", "枝江北", "宜昌东"]

sectionList1 = ["红安西", "麻城北"]


# 单个车站时使用，线路和车站关系，主要用于从车站-值获取线路-键
route12 = {"汉口": hrHankou, "合肥南": hrhefei}
route1Default = ["汉口"]  # 找不到的默认设置


# 单个车站使用，综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entranceRoute = {
    (*hrHankou, *sectionList1, *hrhefei[::-1]): [2,  (1, 1), (1, 2), 2],
    (*jgWuhan, *sectionList1, *hrhefei[::-1]): [2,  (1, 1), (1, 2), 2],
    (*hrHankou, *sectionList1, *hwdetourhefei[::-1]): [2,  (1, 1), (1, 2), 2],
    (*jgWuhan, *sectionList1, *hwdetourhefei[::-1]): [2,  (1, 1), (1, 2), 2],

    (*hrhefei, *sectionList1, *hrHankou[::-1]): [1,  (3, 4), (2, 2), 1],
    (*hrhefei, *sectionList1, *jgWuhan[::-1]): [1,  (3, 4), (2, 2), 1],
    (*hwdetourhefei, *sectionList1, *hrHankou[::-1]): [1,  (3, 4), (2, 2), 1],
    (*hwdetourhefei, *sectionList1, *jgWuhan[::-1]): [1,  (3, 4), (2, 2), 1],
}

entrance1Default = (0, 0, 0, 0, 0, 0)

entranceBlock = {

}

# 按照区间生成个线路时映射使用
# srcdst0 = ["汉口", "宜昌东"]  # .reverse()
# seq0 = 0

# # 可能的径路
# routeList0 = {"station": ["汉口", "武昌", "汉川", "天门南", "仙桃西", "潜江", "荆州", "枝江北", "宜昌东"],
#              "way": ["0", "0", "1", "1", "1", "1", "1", "1", "2"], }
# totaltrain0 = 20

# 按照核心车站生成单个线路映射
srcdstProduce = "襄阳东"  # .reverse()
srcdstConsume = ["襄阳东", "汉口"]
seq = 2  # 1为下行方向，2为上行行方向
# 可能的径路
# 0为出发车站，1为中间站，2为离场车站，3为特殊站即不单纯映射自身等需要特殊处理的
routeList = {"station": ["汉口", "天河机场", "孝感东", "云梦东", "安陆西", "随州南", "随县", "枣阳",
                         "襄阳东", "谷城北", "丹江口", "武当山西", "十堰东", "巴东", "重庆北", "郑州东"][::-1],
             "way": ["2", "1", "1", "1", "1", "1", "1", "1", "3", "1", "1", "1", "0", "0", "0", "0"][::-1], }

totaltrain = 50

# 车辆段，动车所，线路所等，中间标号1为进场时间做减法，-1为离场时间做加法,
# 线路所到达车站。按照进场顺序标定,汉口到十堰东、重庆北顺序
BlockPostAndDepot = {
    "重庆北": [("重庆北", +1, 7, 2), ("东津线路所", +1, 4, 2)],
    "巴东": [("重庆北", +1, 7, 2), ("东津线路所", +1, 4, 2)],

    "襄阳东": [("襄阳东动车所", +1, 30, 0)],
    "十堰东": [("西安东", +1, 20, 1)],
}

# 线路所归属车站
BlockPostBelong = {
    "东津线路所": "襄阳东",
    "重庆北": "襄阳东",
    "襄阳东动车所": "襄阳东",
    "西安东": "十堰东",

}

outfile = "汉十段.txt"
# 生产者1，从路路通程序获取真是车次


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
        # 车站查询输入框
        self.stationquery = self.window.EditControl(
            searchDepth=2, foundIndex=3, AutomationId="1001")
        # self.stationquery.Click()  # 点击以激活输入框
        # 站站查询输入框
        self.fromquery = self.window.EditControl(
            searchDepth=2, foundIndex=1, AutomationId="1001")
        self.toquery = self.window.EditControl(
            searchDepth=2, foundIndex=2, AutomationId="1001")

        # 返回值为0为未选中，返回值1为选中
        self.isoperate = auto.CheckBoxControl(
            searchDepth=2, AutomationId="1024")  # 当日不开行
        if self.isoperate.GetTogglePattern().ToggleState == 1:
            self.isoperate.Click()  # 勾选以隐藏未开行车次

        # 返回值为0为未选中，返回值1为选中
        self.isobscure = auto.CheckBoxControl(
            searchDepth=2, AutomationId="1025")  # 模糊车站

        return

    def selectstation(self, station: str):  # 按照车站查询
        # 车站查询使用精确查找，返回值为0为未选中，返回值1为选中
        if self.isobscure.GetTogglePattern().ToggleState == 1:
            self.isobscure.Click()  # 取消勾选以获得准确单个车站

        self.stationquery.Click()  # 点击以车站查询激活输入框
        self.stationquery.SendKeys('{Ctrl}a{Del}', waitTime=0.1)  # 全选清空内容
        self.stationquery.SendKeys(text=station, waitTime=0.1)  # 输入需要查询的车站名称

        self.quetybtn = self.window.ButtonControl(
            searchDepth=1, foundIndex=1, AutomationId="1006")  # 查询按钮
        self.quetybtn.Click(waitTime=0.1)  # 点击查询按钮

        return

    def selectzone(self, fromsation: str, tostation: str):  # 按照站站区间查询
        # 区间查询采用模糊查找，返回值为0为未选中，返回值1为选中
        if self.isobscure.GetTogglePattern().ToggleState == 0:
            self.isobscure.Click()  # 取消勾选以获得准确单个车站

        self.fromquery.Click()  # 点击以激活区间始发站输入框
        self.fromquery.SendKeys('{Ctrl}a{Del}', waitTime=0.1)  # 全选清空内容
        self.fromquery.SendKeys(text=fromsation, waitTime=0.1)  # 输入需要查询的车站名称

        self.toquery.Click()  # 点击以区间终到站激活输入框
        self.toquery.SendKeys('{Ctrl}a{Del}', waitTime=0.1)  # 全选清空内容
        self.toquery.SendKeys(text=tostation, waitTime=0.1)  # 输入需要查询的车站名称

        self.quetybtn = self.window.ButtonControl(
            searchDepth=1, foundIndex=1, AutomationId="1006")  # 查询按钮
        self.quetybtn.Click(waitTime=0.1)  # 点击查询按钮

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
    pass
# 生产者进程函数


def obtaintrain(lltroute: str, tc: int, station: str | list[str], InfoQueue: Queue, trainCodeQueue: Queue):
    lltpro = lltskbProcess(
        lltskbroute=lltroute, traincount=tc)
    lltpro.initsetting()  # 处理获取时刻表信息
    # 第二个目标站置空则视为单一车站
    if type(station) == str:
        lltpro.selectstation(station=station)
    elif type(station) == list and len(station) == 2:  # 若不为空则为区间,且指定长度为2
        lltpro.selectzone(fromsation=station[0], tostation=station[1])
    else:
        print("参数station:{0}不合法,类型为:{1},期望类型为单一字符串或是两个字符串组成列表".format(
            station, type(station)))
    # 二者查询后续相同
    lltpro.generateroute(InfoQueue, trainCodeQueue)

    return


# 生产者2，生成随机车次,作用和initStrFormate类似

def FakeTrainStrFormate():
    temporateTrainInner = (8000, 8999)
    temporateTrainOuter = (4000, 4999)

    pass


# 消费者1/2 通过原始字符生成游戏样式时刻表
def initStrFormate(initcodeStr: str, initInfoStr: str):
    # 使用最初得到的字符数据
    traincodeStr = initcodeStr.replace("次", "")  # 字符串样式车次便于最后生成游戏样式的字符串
    if traincodeStr[-1] == "B":  # 对于不开行车次
        traincodeStr = traincodeStr.replace("B", "")
    elif traincodeStr[-1] == "C":
        traincodeStr = traincodeStr.replace("C", "")

    traincodeList = traincodeStr.split(sep="/")  # 列表样式便于下面处理
    if len(traincodeList) == 2:  # 如果变化车次，使用0号位车次替代便于一起处理
        initInfoStr = initInfoStr.replace(
            traincodeList[1], traincodeList[0])  # [1:]

    # 按照车次数字部分分割，因为复制过来车次有首位缺失
    initList = initInfoStr.split(traincodeList[0])
    tarposi = 0
    formatInfoList0 = []  # 记录整体信息的二位列表
    formatInfoStr0 = []  # 记录整体信息的一位字符串列表
    for idx, ele in enumerate(initList):
        eleli = ele.split(sep="\t")  # \t武汉东\t21:27\t21:33\t91\t\t\t.....

        midInfo = ["", "", "", "", "", ""]  # 重新定义并清空,车次 停站 到时 开时 里程 检票口
        if len(eleli) >= 5:  # 信息列表长度在5以上的一般是正常信息，反正只记录前几个
            midInfo[0] = traincodeStr  # 记录车次和车站信息
            midInfo[1] = eleli[1]  # 记录停站信息，提前处理始发终到异常信息
            midInfo[2] = eleli[2] if eleli[2] != "-- --"else eleli[3]
            midInfo[3] = eleli[3] if eleli[3] != "-- --"else eleli[2]
            midInfo[4] = eleli[4]  # 里程信息，没啥大用
            midInfo[5] = "0"  # 预留为记录检票口用

            # 加入列表
            formatInfoList0.append(midInfo)  # 一行以列表形式整体加入
            formatInfoStr0 = formatInfoStr0 + midInfo  # 一行信息以字符串形式合并加入整体

        else:
            continue
    return formatInfoList0, formatInfoStr0


# 对于按照车站查询的列车
def stationtrainFormat(station: str, InfoListList: list[list[str]], InfoListStr: list[str]):
    # 目标车站,字符串样式暂时不方便使用index等
    # 获取目标车站在停站信息的位置，暂不考虑环线停靠两次等
    finalli = [[], [], []]  # 返回上一站下一站和当前站
    tarposi = InfoListStr.index(station)
    if tarposi == 1:  # 始发车
        finalli = [InfoListList[0], InfoListList[0], InfoListList[1]]
    elif tarposi == len(InfoListStr)-5:  # 终到车
        finalli = [InfoListList[-2],
                   InfoListList[-1], InfoListList[-1]]
    else:  # 其他
        i = int(tarposi/6)
        finalli = [InfoListList[i-1],
                   InfoListList[i], InfoListList[i+1]]

    # 使用上面初步处理的数据帧并完成进一步处理
    fullRoute2 = []
    centreStIdx = 0
    censt = finalli[1]  # 中心车站位置

    for idx, ele in enumerate(finalli):
        if idx == 0:  # 进场数据映射,进场时间均设置为到站时间
            routemap = route12.get(ele[1], route1Default)
            routeLi = [[ele[0], a, censt[2], censt[2], ele[5], 0]
                       for a in routemap]
            centreStIdx = len(routemap)  # 记录中心车站顺序
        elif idx == 1:  # 停站数据直接合并加入
            routeLi = [[ele[0], ele[1], ele[2], ele[3], ele[5], 1]]
        else:  # 离场路线映射，离场时间均设置为发车时间
            routemap = route12.get(ele[1], route1Default)[::-1]  # 离场需要反转顺序
            routeLi = [[ele[0], a, censt[3], censt[3], ele[5], 2]
                       for a in routemap]
        fullRoute2 += routeLi  # 整理合并加入
    return fullRoute2

# 对于按照区间查询的列车


def sectiontrainFormat(sectionstations: list, InfoListList: list[list[str]], InfoListStr: list[str]):
    # 区间内所有车站名称
    sectionst = pandas.DataFrame(
        data=routeList, columns=["station", "way"])
    # 单一车次
    trainst = pandas.DataFrame(data=InfoListList, columns=[
        "traincode", "station", "arrival", "departure", "entrance", "drop0"])
    trainst.drop(columns="drop0", inplace=True)
    # 合并二者
    sectionTrain = pandas.merge(
        left=sectionst, right=trainst, how="inner", on=["station"], suffixes=("", ""))
    return sectionTrain


def mapArrLeaTime(t1: pandas.Timestamp, st: str, mark: int) -> pandas.Timestamp:
    # 选取是进场还是立场
    useTime = gameStationInfo.get(st, gameStationDefault)[3]
    if mark == 0:  # 进场减时间
        res = t1-datetime.timedelta(minutes=useTime)
    else:  # 离场加时间
        res = t1+datetime.timedelta(minutes=useTime)
    # 返回时分秒格式的字符串
    return res


def mapEntrance0(df: pandas.DataFrame) -> list:
    # 改为元组来作为key查找
    routekey = tuple(df["station"].to_list())
    waykey = df["way"].to_list()
    entranceList = []
    try:  # 映射径路
        routelist = entranceRoute[routekey]
    except Exception:
        print("径路**{r}**未收录".format(r=routekey))
        entranceList = [0]*len(waykey)
    else:
        for i in range(0, len(waykey)):
            if waykey[i] == 1:  # 停站部分使用随机数
                entranceList.append(random.randint(
                    routelist[i][0], routelist[i][1]))
            else:  # 其他的则直接加入
                entranceList.append(routelist[i])

    return entranceList


def mapEntrance1(station: str, way: str, fromto=seq) -> int:
    truckrange = gameStationInfo.get(station, gameStationDefault)
    if way == "0":
        idx = 1
    elif (way == "1" or way == "3") and fromto == 1:
        idx = 1
    elif (way == "1" or way == "3") and fromto == 2:
        idx = 2
    elif way == "2":
        idx = 2
    res = random.randint(truckrange[idx][0], truckrange[idx][1])
    return res


def mapStationCode(st: str, traincode: str) -> str:
    stationCode = []
    try:
        stationInfo = gameStationInfo[st]
    except KeyError:
        print("**{a}**车次**{b}**车站未收录".format(a=traincode, b=st))
        stationCode = gameStationDefault[0]
    else:
        stationCode = stationInfo[0]  # type: ignore

    return stationCode


def AdditionStationStr(specialrow, l):
    sp = BlockPostAndDepot.get(specialrow.station, [])
    specialStr = ["" for _ in range(0, len(sp))]  # 记录相对中心车站的位置
    routeStr = ""

    pass

    # 满足如下条件则是车辆段终到车
    if specialrow.Index == 0:
        specialStr = specialStr[::-1]

    return " ".join(specialStr)


def additionBlockDepot(df: pandas.DataFrame, fromto=seq) -> pandas.DataFrame:
    d1 = ["traincode", "station", "arrival",
          "departure", "entrance"]
    blockdict = {k: [] for k in d1}

    for row in df.itertuples(index=True):
        bp = BlockPostAndDepot.get(row.station, None)  # type: ignore
        if bp == None:  # 非特殊站点
            continue
        elif row.station == srcdstProduce and (row.Index != 0 or row.Index != len(df)-1):
            continue  # 不满足始发终到条件
        else:
            for eachbp in bp:  # 线路所或者是符合始发终到条件
                blockinfo = gameStationInfo.get(eachbp[0], gameStationDefault)
                # 对应线路所和车站信息
                blockdict["traincode"].append(row.traincode)
                blockdict["station"].append(eachbp[0])
                # 线路所归属车站
                stationBelongto = df[df["station"]
                                     == BlockPostBelong[eachbp[0]]]
                stationBelongto.reset_index(inplace=True)
                blockdict["arrival"].append(
                    stationBelongto.at[0, "arrival"]-eachbp[1]*datetime.timedelta(minutes=eachbp[2]))  # type: ignore
                blockdict["departure"].append(
                    stationBelongto.at[0, "departure"]-eachbp[1]*datetime.timedelta(minutes=eachbp[2]))  # type: ignore
                blockdict["entrance"].append(eachbp[3])

                # 加入停站时间和标记
    if len(blockdict["traincode"]) != 0:  # 带有线路所则执行拼接操作
        blockdict["way"] = ["2"]*len(blockdict["traincode"])
        blockdict["stoptime"] = [0]*len(blockdict["traincode"])
        blockdf = pandas.DataFrame(data=blockdict)

        # 在原时刻表中删去特殊车站
        stopstationdf = df[~df["station"].isin(blockdict["station"])]

        traindf = pandas.concat(
            objs=[stopstationdf, blockdf], axis="index", ignore_index=True)
        return traindf
    else:  # 没有则无需执行
        return df


def routeStrFormate(fullRoute2: list[list] | pandas.DataFrame):

    # 规整时间格式，改为时间戳以完成计算
    col = ["traincode", "station", "arrival", "departure", "entrance", "way"]
    traindf = pandas.DataFrame(data=fullRoute2, index=None, columns=col)

    traindf["arrival"] = pandas.to_datetime(
        arg=traindf["arrival"],  format="%H:%M")
    traindf["departure"] = pandas.to_datetime(
        arg=traindf["departure"],  format="%H:%M")
    # 计算停站时间，并将浮点数改为分钟整数
    traindf["stoptime"] = (traindf["departure"] -
                           traindf["arrival"]).dt.total_seconds() / 60

    traindf.reset_index(inplace=True)

    if type(fullRoute2) == list:  # 传入列表即为单个车站的车次样式
        centreStIdx = len(fullRoute2[0])
        # 对于单一车站映射对应进场立场时间，同时转换为字符串
        traindf["arrival"] = traindf.apply(lambda x: mapArrLeaTime(
            t1=traindf.iloc[centreStIdx, 2], st=x["station"], mark=0), axis=1)  # type: ignore
        traindf["departure"] = traindf.apply(lambda x: mapArrLeaTime(
            t1=traindf.iloc[centreStIdx, 3], st=x["station"], mark=1), axis=1)  # type: ignore
        # 对于非中心车站进行映射
        traindf["entrance"] = mapEntrance0(traindf)
    elif type(fullRoute2) == pandas.DataFrame:  # 其他即dataframe即为线路
        # 对于简单区间映射对应进场立场时间，同时转换为字符串
        # 这部分需要额外修改加入进场时间和离场时间，即修改区间始末站点

        traindf["entrance"] = traindf.apply(
            lambda x: mapEntrance1(x["station"], x["way"]), axis="columns")
        traindf = additionBlockDepot(traindf)  # 线路所等

    # 映射车站为对应字母编号
    traindf["station"] = traindf.apply(
        lambda x: mapStationCode(x["station"], x["traincode"]), axis=1)
    traindf["stoptime"] = traindf["stoptime"].apply(lambda x: int(x))
    traindf.drop_duplicates(
        keep="last", inplace=True)
    return traindf
#

# 生成线路所和车辆段，动车所始发终到字符，进需要使用位置判断，位于开始或者结束
#


def generateGameStr(infodf: pandas.DataFrame):
    # 最后生成游戏字符串，entrule为股道/检票口在entrance部分的位置范围

    trcode = infodf["traincode"][0]
    trtype = trcode[0]

    typeInfo = species1.get(trtype, species1default)
    trainStr = "{tc} URBAN {spe} {mar} X1 :".format(
        tc=trcode, spe=typeInfo[0], mar=typeInfo[1])
    routeStrList = [trainStr]
    routeStr = ""
    if infodf.at[0, "arrival"] >= infodf.at[1, "arrival"]:
        return ""
    else:
        infodf.sort_values(by=["arrival", "departure"],
                           inplace=True, ignore_index=True)
        print(infodf)
    flag = 0  # 理论上应该至少会停靠一个非特殊中间车站
    for row in infodf.itertuples(index=True):
        if row.way == "0":  # 进场
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=row.entrance, clck=row.departure.strftime("%H:%M:%S"), stay=row.stoptime)   # type: ignore
        elif row.way == "1":  # 停靠
            flag = 1
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=row.entrance, clck=row.arrival.strftime("%H:%M:%S"), stay=row.stoptime)  # type: ignore
        else:   # 离场
            routeStr = "{sta}#{rail}#{clck}#{stay}".format(
                sta=row.station, rail=row.entrance, clck=row.arrival.strftime("%H:%M:%S"), stay=row.stoptime)  # type: ignore
        if routeStr != routeStrList[-1]:  # 解决莫名其妙的重复
            routeStrList.append(routeStr)
        else:
            continue

    if flag == 0:  # 一个区间车站都不停的一般都是其他线路的车
        return ""
    else:
        ret = " ".join(routeStrList)
        print(ret)
        return ret


def gameStrProcess(station: str | list[str], InfoQueueCons: Queue, trainCodeQueueCons: Queue, outfile: str):
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
        initlistlist, initliststr = initStrFormate(
            initcodeStr=initcode, initInfoStr=initInfo)

        if type(station) == str:
            initpr2 = stationtrainFormat(
                station=station, InfoListList=initlistlist, InfoListStr=initliststr)
        elif type(station) == list:
            initpr2 = sectiontrainFormat(
                sectionstations=station, InfoListList=initlistlist, InfoListStr=initliststr)
        nextpr2 = routeStrFormate(fullRoute2=initpr2)
        outstr = generateGameStr(nextpr2)
        resset.add(outstr)  # 加入最后文件

    f = open(file=outfile, mode="w", encoding="utf-8")
    for rs in resset:  # 写入文件
        f.write(rs+"\n")
    f.close()
    return


def strReproduct(file1: str, file2: str):
    codelist = []  # 去重以及调整顺序
    infolist = []
    with open(file=file1, mode="r", encoding="utf-8") as f:
        for li in f:
            info1 = li
            code1 = li.split(sep=" ", maxsplit=1)[0]
            if code1 not in codelist:  # 按照车次去重部分
                codelist.append(code1)
                infolist.append(info1)
            else:
                continue
    f.close()
    infolist.sort()  # 重新排序
    with open(file=file2, mode="a", encoding="utf-8") as w:
        for i in infolist:
            w.writelines(i)
    w.close()

    return


if __name__ == "__main__":
    InfoQueue1 = multiprocessing.Queue()  # 径路信息队列
    trainCodeQueue1 = multiprocessing.Queue()  # 车次号队列
    # 中继承接队列

    # 生产者进程，中间的totaltrain为当前车站车次总数，约数即可
    # srcdst为单一车站字符时按单一车站处理，如果为始发终到站列表则按照区间处理
    # p = multiprocessing.Process(
    #     target=obtaintrain, args=(lltskbroute, totaltrain, srcdstConsume, InfoQueue1, trainCodeQueue1,))

    # c = multiprocessing.Process(
    #     target=gameStrProcess, args=(srcdstConsume, InfoQueue1, trainCodeQueue1, "midfile.txt"))# 消费者进程

    # p.start()  # 启动生产者和消费者进程
    # time.sleep(10)  # 启动较慢，等待生产者初始化完成
    # c.start()

    # p.join()  # 等待生产者进程完成
    # InfoQueue1.put("114514")  # magic number,通知消费者所有产品已经生产完毕
    # c.join()  # 等待消费者进程完成

    # strReproduct("midfile.txt", outfile)  # 重整结果便于合并立折车次

    strReproduct("汉十高速至襄阳东.txt", "汉十高速全天.txt")
    ''''''

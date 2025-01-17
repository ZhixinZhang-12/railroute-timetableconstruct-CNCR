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
# a = 武昌站 | 1 | 2, 1, 4, 3, 5, 6, 7, 8, 9 
# b = 京广线汉口(外绕)/孝感方向 | 1 | 2, 1 
# c = 汉西联络线至新墩汉川应城荆门 | 1 | 1, 2 
# d = 京广线咸宁方向 | 1 | 1, 2 
# e = 武咸城际南湖东方向 | 1 | 1, 2 
# f = 武昌南环线何流鄂州方向 | 1 | 1, 2 
# g = 武客技 | 1 | 2, 1 
# h = 京广三四线至武昌南货场 | 1 | 2, 1 
# i = 武昌北环线楠姆庙方向(已废弃) | 1 | 1 
# j = 武汉长江大桥 | 1 |  
# k = 汉西 | 1 | 5, 4, 3, 1, 2 
# l = 汉阳 | 1 | 3, 4, 1, 2 
# m = 汉口汉西联络线至汉口站 | 1 | 1 
# n = 余家湾 | 1 | 4, 3, 1, 2 

 
905|905 COMMUTER 120 LPPPL X1 : c#1#08:00:00#0 k#2#08:03:00#0 a#6#08:06:00#0 l#2#08:10:00#0 d#1#08:14:00#0
535|535 COMMUTER 120 LPPPL X1 : e#0#08:00:00#0 a#0#08:15:00#3 c#0#08:24:00#0
846|846 COMMUTER 120 LPPPL X1 : f#0#08:00:00#0 a#0#08:15:00#1 c#2#08:22:00#0
623|623 COMMUTER 120 LPPPL X1 : e#2#08:00:00#0 f#0#08:05:00#0
878|878 COMMUTER 120 LPPPL X1 : b#0#00:00:00#0 a#8#00:04:00#0 c#0#00:09:00#0
831|831 COMMUTER 120 LPPPL X1 : c#1#08:00:00#0 a#0#08:06:00#6 d#1#08:18:00#0
URBAN
'''

# 速度和编组以及类型映射关系,0为普速1为动车2为高速，后续修改
species1 = {'K': ['120', 'LCPPPPPPPP', "0"], 'T': ['140', 'LCPPPPPPPP', "0"], 'Z': ['160', 'LCPPPPPPPP', "0"],
            'D': ['250', 'LLPLPPLL', "1"], 'C': ['200', 'LPPL', "1"], 'G': ['350', 'LPLPPLPL', "2"]}
species1default = ['120', 'LCPPPPPPPP', "0"]
# 游戏里放16编组的实在是太长了，所以目前还是不准备使用对应编组爬取部分
marshalling = {"": ""}

# d = 焦柳线松滋方向 | 1 | 1, 2 枝城 松滋 张家界 石门县北
# f = 焦柳线荆门方向
# 车站-编号,进场立场股道,用时
# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
# 对于股道，若为边界进出场车站股道为进场立场行走股道编号，若为越行站则为对应正线、越行线编号
gameStationInfo = {'武昌': ['a', 0, 0, 0],
                   '京广线汉口方向': ['b', 1, 2, 10], '汉西联络线': ['c', 1, 2, 10],
                   '汉口汉西联络线至汉口站': ['m', 1, 2, 10],
                   '京广线咸宁方向': ['d', 2, 1, 8],
                   '武昌南环线何流方向': ['f', 2, 1, 10],
                   '武咸城际南湖东方向': ['e', 2, 1, 5],
                   '武客技': ['g', 0, 0, 20],

                   '汉西': ['k', 1, 2, 8], '汉阳': ['l', 1, 2, 5],
                   '余家湾': ['n', 2, 1, 5],
                   }
gameStationDefault = ['g',  0, 0, 20]  # 找不到的默认设置

# 线路和车站关系，主要用于从车站-值获取线路-键
route12 = {'应城': ['汉西联络线', "汉西", "汉阳"], '天门': ['汉西联络线', "汉西", "汉阳"],
           '京山': ['汉西联络线', "汉西", "汉阳"], '钟祥': ['汉西联络线', "汉西", "汉阳"], '云梦': ['汉西联络线', "汉西", "汉阳"],
           '安陆': ['汉西联络线', "汉西", "汉阳"], '随州': ['汉西联络线', "汉西", "汉阳"],
           '枣阳': ['汉西联络线', "汉西", "汉阳"], '襄阳': ['汉西联络线', "汉西", "汉阳"], '汉川': ['汉西联络线', "汉西", "汉阳"], '天门南': ['汉西联络线', "汉西", "汉阳"], '仙桃': ['汉西联络线', "汉西", "汉阳"], '仙桃西': ['汉西联络线', "汉西", "汉阳"], '潜江': ['汉西联络线', "汉西", "汉阳"],

           '郑州': ['京广线汉口方向', "汉西", "汉阳"], '许昌': ['京广线汉口方向', "汉西", "汉阳"], '信阳': ['京广线汉口方向', "汉西", "汉阳"], '漯河': ['京广线汉口方向', "汉西", "汉阳"],
           '驻马店': ['京广线汉口方向', "汉西", "汉阳"], '长葛': ['京广线汉口方向', "汉西", "汉阳"], '花园': ['京广线汉口方向', "汉西", "汉阳"], '孝感': ['京广线汉口方向', "汉西", "汉阳"], '广水': ['京广线汉口方向', "汉西", "汉阳"], '麻城': ['京广线汉口方向', "汉西", "汉阳"],

           '咸宁': ['京广线咸宁方向', "余家湾"], '赤壁': ['京广线咸宁方向', "余家湾"], '临湘': ['京广线咸宁方向', "余家湾"], '岳阳': ['京广线咸宁方向', "余家湾"], '长沙': ['京广线咸宁方向', "余家湾"],
           '广州': ['京广线咸宁方向', "余家湾"], '广州东': ['京广线咸宁方向', "余家湾"], '深圳': ['京广线咸宁方向', "余家湾"],

           '南湖东': ['武咸城际南湖东方向', "余家湾"], '武汉东': ['武咸城际南湖东方向', "余家湾"], '葛店南': ['武咸城际南湖东方向', "余家湾"],
           '庙山': ['武咸城际南湖东方向', "余家湾"], '纸坊东': ['武咸城际南湖东方向', "余家湾"], '汤逊湖': ['武咸城际南湖东方向', "余家湾"],

           '鄂州': ['武昌南环线何流方向', "余家湾"], '黄石': ['武昌南环线何流方向', "余家湾"], '阳新大冶': ['武昌南环线何流方向', "余家湾"], '南昌': ['武昌南环线何流方向', "余家湾"],
           '汉口': ['汉口汉西联络线至汉口站', "汉西", "汉阳"],
           '武昌': ['武客技']}

route1Default = ["武客技"]  # 找不到的默认设置

# 综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entrance12 = {
    ("汉西联络线", "汉西", "汉阳", "武昌", "余家湾", "京广线咸宁方向"): [1, 3, 1, (5, 9), 1, 1],
    ("汉西联络线", "汉西", "汉阳", "武昌", "余家湾", "武昌南环线何流方向"): [1, 3, 1, (5, 9), 1, 1],
    ("汉西联络线", "汉西", "汉阳", "武昌", "余家湾", "武咸城际南湖东方向"): [1, 3, 1, (5, 9), 3, 1],

    ("京广线汉口方向", "汉西", "汉阳", "武昌", "余家湾", "武昌南环线何流方向"): [1, 1, 1, (5, 9), 1, 1],
    ("京广线汉口方向", "汉西", "汉阳", "武昌", "余家湾", "武咸城际南湖东方向"): [1, 1, 1, (5, 9), 3, 1],
    ('京广线汉口方向', '汉西', '汉阳', '武昌', '余家湾', '京广线咸宁方向'): [1, 1, 1, (5, 9), 1, 1],

    ("汉口汉西联络线至汉口站", "汉西", "汉阳", "武昌", "余家湾", "京广线咸宁方向"): [1, 1, 1, (5, 9), 1, 1],
    ("汉口汉西联络线至汉口站", "汉西", "汉阳", "武昌", "余家湾", "武昌南环线何流方向"): [1, 1, 1, (5, 9), 1, 1],
    ("汉口汉西联络线至汉口站", "汉西", "汉阳", "武昌", "余家湾", "武咸城际南湖东方向"): [1, 1, 1, (5, 9), 3, 1],

    ("京广线咸宁方向", "余家湾", "武昌", "汉阳", "汉西", "汉西联络线"): [2, 2, (1, 4), 2, 4, 2],
    ("京广线咸宁方向", "余家湾", "武昌", "汉阳", "汉西", "京广线汉口方向"): [2, 2, (1, 4), 2, 2, 2],
    ("京广线咸宁方向", "余家湾", "武昌", "汉阳", "汉西", "汉口汉西联络线至汉口站"): [2, 2, (1, 4), 2, 2, 2],

    ("武昌南环线何流方向", "余家湾", "武昌", "汉阳", "汉西", "汉西联络线"): [2, 2, (1, 4), 2, 4, 2],
    ("武昌南环线何流方向", "余家湾", "武昌", "汉阳", "汉西", "京广线汉口方向"): [2, 2, (1, 4), 2, 2, 2],
    ("武昌南环线何流方向", "余家湾", "武昌", "汉阳", "汉西", "汉口汉西联络线至汉口站"): [2, 2, (1, 4), 2, 2, 2],

    ("武咸城际南湖东方向", "余家湾", "武昌", "汉阳", "汉西", "汉西联络线"): [2, 4, (1, 4), 2, 4, 2],
    ("武咸城际南湖东方向", "余家湾", "武昌", "汉阳", "汉西", "京广线汉口方向"): [2, 4, (1, 4), 2, 2, 2],
    ("武咸城际南湖东方向", "余家湾", "武昌", "汉阳", "汉西", "汉口汉西联络线至汉口站"): [2, 4, (1, 4), 2, 2, 2],

    ("汉西联络线", "汉西", "汉阳", "武昌", "武客技"): [1, 3, 1, (5, 9),  2],
    ("京广线汉口方向", "汉西", "汉阳", "武昌", "武客技"): [1, 1, 1, (5, 9),  2],
    ("武客技", "武昌", "汉阳", "汉西", "汉西联络线"): [1, (1, 4), 2, 4, 2],
    ("武客技", "武昌", "汉阳", "汉西", "京广线汉口方向"): [1, (1, 4), 2, 2, 2],

    ("武昌南环线何流方向", "余家湾", "武昌", "武客技"): [2, 2, (1, 4), 1],
    ("京广线咸宁方向", "余家湾", "武昌", "武客技"): [2, 2, (1, 4), 1],
    ("武客技", "武昌", "余家湾", "京广线咸宁方向"): [1, (5, 9), 1, 1],
    ("武客技", "武昌", "余家湾", "武昌南环线何流方向"): [1, (5, 9), 1, 1],

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
    formatInfoList0 = []  # 记录整体信息的二位列表
    formatInfoStr0 = []  # 记录整体信息的一位字符串列表
    for idx, ele in enumerate(initList):
        eleli = ele.split(sep="\t")  # \t武汉东\t21:27\t21:33\t91\t\t\t.....

        midInfo = ["", "", "", "", ""]  # 重新定义并清空
        if len(eleli) >= 5:  # 信息列表长度在5以上的一般是正常信息，反正只记录前几个
            midInfo[0] = traincodeStr  # 记录车次和车站信息
            midInfo[1] = eleli[1]  # 记录停站信息，提前处理始发终到异常信息
            midInfo[2] = eleli[2] if eleli[2] != "-- --" else eleli[3]
            midInfo[3] = eleli[3] if eleli[3] != "-- --" else eleli[2]
            midInfo[4] = eleli[4]  # 里程信息，没啥大用，预留为记录检票口用
            # 加入列表
            formatInfoList0.append(midInfo)  # 以列表形式整体加入

            formatInfoStr0 = formatInfoStr0 + midInfo  # 以字符串形式合并加入

        else:
            continue

        # 目标车站,字符串样式暂时不方便使用index等
        # 获取目标车站在停站信息的位置，暂不考虑环线停靠两次等
    print(formatInfoStr0)
    finalli = [[], [], []]#返回上一站下一站和当前站
    tarposi = formatInfoStr0.index(station)
    if tarposi == 1:  # 始发车
        finalli = [formatInfoList0[0], formatInfoList0[0], formatInfoList0[1]]
    elif tarposi == len(formatInfoStr0)-4:  # 终到车
        finalli = [formatInfoList0[-2],
                   formatInfoList0[-1], formatInfoList0[-1]]
    else:  # 其他
        i = int(tarposi/5)
        finalli = [formatInfoList0[i-1],
                   formatInfoList0[i], formatInfoList0[i+1]]
    print(finalli)
    return finalli


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
    trainStr = "{tc} URBAN {spe} {mar} X1 :".format(
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
    targetstation = "黄冈东"
    strtest = "D5885	汉口	-- --	07:02	0	D5885	武汉	07:28	07:45	31	D5885	黄冈东	08:17	-- --	96																																			"
    lltskbroute = "lltskb\\lltskb.exe"
    initpr1 = initStrFormate(
        station=targetstation, initcodeStr="D5885", initInfoStr=strtest)
'''
    # initpr1 = initStrFormate(
    #     station=targetstation, initcodeStr="D5801", initInfoStr=strtest)
    # nextpr2 = routeStrFormate(prepareList=initpr1)
    # outstr = generateGameStr(nextpr2)
    p = multiprocessing.Process(
        target=obtaintrain, args=(lltskbroute, 200, targetstation, InfoQueue1, trainCodeQueue1,))
    c = multiprocessing.Process(
        target=gameStrProcess, args=(targetstation, InfoQueue1, trainCodeQueue1, "text2.txt"))

    p.start()  # 启动生产者和消费者进程
    time.sleep(10)  # 启动较慢，等待生产者初始化完成
    c.start()

    p.join()  # 等待生产者进程完成
    InfoQueue1.put("114514")  # magic number,通知消费者所有产品已经生产完毕
    c.join()  # 等待消费者进程完成
    strReproduct("text2.txt", "武昌1.txt")

'''

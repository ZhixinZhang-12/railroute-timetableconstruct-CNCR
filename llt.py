<<<<<<< HEAD
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.android.nativekey import AndroidKey
from appium.webdriver.common.touch_action import TouchAction
import appium
from pyecharts import options as opts
from pyecharts.charts import Bar, Timeline
import random
import itertools
import pandas
import matplotlib
import pyecharts
import numpy
import time
import datetime
import plotly.figure_factory as ff
# 每一个车站的所有停车信息


def StationTrainList(driver: WebDriver, action: TouchAction, station: str):
    time.sleep(8)  # 等待开屏广告
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车站")')

    action.tap(stationText).perform()  # 点击车站选项的位置

    stationChk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/layout_station")  # 车站选择部分
    action.tap(stationChk).perform()  # 进入车站选择
    time.sleep(1)
    stationSelect = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/edit_input")  # 车站选择输入框
    stationSelect.send_keys(station)  # 输入

    stationFind = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("{0}")'.format(station))
    action.tap(stationFind[1]).perform()  # 输入车站名并确认，返回之前的页面

    searchbtn = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/querycz_btn")  # 搜索按钮
    action.tap(searchbtn).perform()  # 点选进行查找
    time.sleep(2)
    # 当前页面可视的车次部分
    pt = driver.find_element(AppiumBy.CLASS_NAME, 'android.widget.ListView')
    x1 = pt.size['width'] * 0.5
    y1 = pt.size['height']  # 获取页面宽高,方便后续滑动截取车次信息

    f = open(file="{0}Info.txt".format(station), mode="w", encoding="utf-8")
    # 设置为utf8，防止如复兴号，静音动车等符号导致报错
    settext = set()  # 使用set尽可能减少重复值

    while True:  # 滑动截取文字
        # 所有有文本的元素的集合，均为当前可见部分
        pageTrainList = driver.find_elements(
            AppiumBy.CLASS_NAME, 'android.widget.TextView')
        beforeSwipe = driver.page_source

        text = ""
        for i in range(0, len(pageTrainList)-9):  # 排除表头信息，仅保留车次部分
            text = text+pageTrainList[i+9].text+","  # 获取整体信息
            if (i+9) % 8 == 0:

                settext.add(text+"\n")
                text = ""

        try:
            # 这里模拟器的分辨率是1920*1080的手机屏幕
            # 如果内容少于一屏幕会直接报错，故使用try
            action.long_press(
                x=540, y=1800, duration=200).move_to(x=540, y=100).release()
            action.perform()  # 在中间滑动，选取新的车次信息
        # 如果滑动前后的元素相同，则表示已经到底了
        except Exception:  # 少于一屏幕就表示已经完成了
            break
        else:  # 前后的页面元素一样
            if driver.page_source == beforeSwipe:
                break
    for it in settext:
        f.write(it)            
    f.close()

    return

# 一组一列车的所有停站信息


def TrainStationList(driver: WebDriver, action: TouchAction, trainli: list[str]):
    time.sleep(8)  # 等待开屏广告
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车次")')
    action.tap(stationText).perform()  # 点击车次选项的位置

    stationchk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/chk_jpk")
    action.tap(stationchk).perform()  # 点选查找检票口选项
    # 设置为utf8，防止如复兴号，静音动车等符号导致报错
    f = open(file="{0}sInfo.txt".format(trainli[0]), mode="w", encoding="utf-8")
    settext = set()  # 使用set尽可能减少重复值
    for train in trainli:
        trainSelect = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/edit_train")
        trainSelect.clear()  # 清空内容防止重输
        trainSelect.send_keys(train)  # 输入查找车次

        searchbtn = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/querycc_btn")  # 搜索按钮
        action.tap(searchbtn).perform()  # 点选进行查找

        text = ""
        while True:  # 进入页面
            beforeSwipe = driver.page_source
# 当前页面上所有“查询”按钮，目前除了全部重复点一遍没有好办法
            searchbtns = driver.find_elements(
                AppiumBy.ID, "com.lltskb.lltskb:id/btn_query")  # 搜索按钮
            for btn in searchbtns:
                action.tap(btn).perform()  # 点选所有按钮进行查找
            pageStationList = driver.find_elements(
                AppiumBy.CLASS_NAME, 'android.widget.TextView')

           # 获取页面所有信息
            for i in range(1, len(pageStationList)):
                # 停站，到时，开时，检票口共四个停站信息
                text = text+pageStationList[i].text+","
                if i % 4 == 0:  # 每一个车站
                    text = train+","+text+"\n"

                    settext.add(text)
                    text = ""
            try:
                # 这里模拟器的分辨率是1920*1080的手机屏幕
                # 如果内容少于一屏幕会直接报错，故使用try
                action.long_press(
                    x=540, y=1800, duration=200).move_to(x=540, y=100).release()
                action.perform()  # 在中间滑动，选取新的车次信息
            # 如果滑动前后的元素相同，则表示已经到底了
            except Exception:  # 少于一屏幕就表示已经完成了
                break
            else:  # 前后的页面元素一样
                if driver.page_source == beforeSwipe:
                    break
        # 按下返回按键，进行下一次查找
        retbtn = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/btn_back")
        action.tap(retbtn).perform()
        # 替换两个汉字，方便后续操作
    for it in settext:
        it = it.replace("到", "").replace("开", "")
        f.write(it)
    f.close()

    return


def StationScreenList(driver: WebDriver, action: TouchAction, train: str):
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车站")')

    action.tap(stationText).perform()  # 点击车站选项的位置

    stationChk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/btn_big_screen")  # 车站大屏选择
    action.tap(stationChk).perform()  # 车站大屏内容部分

    return


def processStation(fn: str)->pandas.DataFrame:

    # 读取文件，设置列名便于后续操作
    stationFrame = pandas.read_csv(filepath_or_buffer=fn,
                                   sep=",", encoding="utf-8")
    stationFrame.columns = ["车次", "drop1", "停站",
                            "到时", "开时", "始发站", "终到站", "列车类型", "drop2"]

    # 删去重复列和空列
    stationFrame.drop_duplicates(inplace=True)
    stationFrame.drop(columns=["drop1", "drop2"], inplace=True)
    stationFrame = dealTime(stationFrame)
    stationFrame["到时-小时"] = numpy.nan
    # print(stationFrame.head())

    for index, row in stationFrame.iterrows():
        stationFrame["到时-小时"][index] = row["到时"].hour

    return stationFrame


def dealTime(datafr: pandas.DataFrame, at="到时", lt="开时") -> pandas.DataFrame:
    # 对于始发车和终到车进行时间处理，默认相同
    for index, row in datafr.iterrows():
        if row[at] == "--:--":
            row[at] = row[lt]
        elif row[lt] == "--:--":
            row[lt] = row[at]

    # 计算停站时间
    datafr["到时"] = pandas.to_datetime(datafr["到时"])
    datafr["开时"] = pandas.to_datetime(datafr["开时"])
    datafr["停站时间"] = datafr["开时"]-datafr["到时"]
    # 实发终到设置停站时间
    # pd["停站时间"].replace(0,10,inplace=True)

    return datafr


trainType = ["新空调快速", "新空调特快", "新空调直快", "动车", "高速", "城际"]
stationRegion = ["济南", "济南西", "济南东", "大明湖"]

# 对于该车站群组（地区）时间段内的所有车次信息


def getStationProid(datafr: pandas.DataFrame, at: int) -> dict:
    # 预先分类
    datagruop = datafr.groupby(["到时-小时", "停站", "列车类型"])
    # print(datagruop.groups)
    regionInfo = {}

    # 对于每个车站的每种类型的列车
    for sr in stationRegion:
        # 好像只能分开写两层了
        regionInfo[sr+"trainCode"] = []
        regionInfo[sr+"trainCount"] = []
        for tt in trainType:
            try:  # 查找符合条件的群组
                i = datagruop.get_group((at, sr, tt))

            except KeyError:  # 索引找不到就是0
                regionInfo[sr+"trainCount"].append(0)
                # regionInfo["trainCode"].append(None)
            else:  # 如果没问题，添加回去长度

                regionInfo[sr+"trainCode"].append(i["车次"].tolist())
                regionInfo[sr+"trainCount"].append(len(i))
        regionInfo[sr+"trainCode"] = sum(regionInfo[sr+"trainCode"], [])
    # 解包嵌套的列表
    # print(regionInfo)

    return regionInfo


def getTrainProid(datafr: pandas.DataFrame, at: int) -> dict:
    # 预先分类
    datagruop = datafr.groupby(["到时-小时", "停站", "列车类型"])
    # print(datagruop.groups)
    regionInfo = {}

    # 对于每个车站的每种类型的列车
    for tt in trainType:
        # 好像只能分开写两层了
        regionInfo[tt+"trainCode"] = []
        regionInfo[tt+"stationName"] = []
        regionInfo[tt+"stationCount"] = []
        for st in stationRegion:
            try:  # 查找符合条件的群组
                i = datagruop.get_group((at, st, tt))

            except KeyError:  # 索引找不到就是0
                regionInfo[tt+"stationCount"].append(0)
                # regionInfo["trainCode"].append(None)
            else:  # 如果没问题，添加回去长度
                regionInfo[tt+"trainCode"].append(i["车次"].tolist())
                regionInfo[tt+"stationName"].append(i["停站"].tolist())
                regionInfo[tt+"stationCount"].append(len(i))

        regionInfo[tt+"stationName"] = sum(regionInfo[tt+"stationName"], [])
    # 解包嵌套的列表
    # print(regionInfo)

    return regionInfo


def drawBarPieSingle(traindf: pandas.DataFrame, seltime: int) -> pyecharts.charts.Bar:
    ri = getTrainProid(traindf, seltime)
    bar = (
        pyecharts.charts.Bar(init_opts=opts.InitOpts(
            width="1000pt", height="500pt"))
        .add_xaxis(stationRegion)  # 按照地区来获取
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(  # 倾斜名称，防止过场重叠
                axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(
                min_interval=2,  # 设置最小间距
                axislabel_opts=opts.LabelOpts()),
            title_opts=opts.TitleOpts(
                "济南地区停车数量 目前时间: {} 时".format(seltime)))
    )

    s1 = []  # 按照停站来统计列车数量
    for st in trainType:
        if len(st) > 3:  # 普速
            bar.add_yaxis(
                series_name=st, y_axis=ri[st+"stationCount"], stack="普速", label_opts=opts.LabelOpts(position="inside"))
        else:  # 高速
            bar.add_yaxis(series_name=st,
                          y_axis=ri[st+"stationCount"], stack="高速", label_opts=opts.LabelOpts(position="inside"))
        s1.append(ri[st+"stationName"])

    s2 = [len(i) for i in s1]  # 每一种列车的数量

    pie = (pyecharts.charts.Pie(init_opts=opts.InitOpts()
                                ).add(
        series_name="",  # 饼图参数，数据对为（列车类型，数量）
        data_pair=[list(z) for z in zip(trainType, s2)],
        radius=["10%", "30%"],
        center=["80%", "20%"],  # 设置大小和位置
        rosetype="radius",
        label_opts=opts.LabelOpts(is_show=True),
    )
    )
    # 重叠
    return bar.overlap(chart=pie)


def drawBarPieCount(traindf: pandas.DataFrame, ) -> pyecharts.charts.Timeline:
    timelic = pyecharts.charts.Timeline()
    totalTr = {}
    for i in range(0, 25):
        ri = getTrainProid(traindf, i)  # 按照车次来获取数据
        bar = (
            pyecharts.charts.Bar(init_opts=opts.InitOpts(
                width="1000pt", height="500pt"))
            .add_xaxis(stationRegion)  # 按照地区添加x轴

            .set_global_opts(  # 设置图表全局参数
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(
                    min_interval=2,
                    axislabel_opts=opts.LabelOpts()),
                title_opts=opts.TitleOpts(
                    title="济南地区停车数量 目前时间: {} 时".format(i)))
        )

        for st in trainType:  # 按照车辆类型分类
            if i == 0:
                totalTr[st+"stationCount"] = ri[st+"stationCount"]
            else:
                totalTr[st+"stationCount"] = [si+sj for si,
                                              sj in zip(totalTr[st+"stationCount"], ri[st+"stationCount"])]

            if len(st) > 3:  # 普速
                bar.add_yaxis(
                    series_name=st, y_axis=totalTr[st+"stationCount"], stack="普速", label_opts=opts.LabelOpts(position="inside"))
            else:  # 高速
                bar.add_yaxis(series_name=st,
                              y_axis=totalTr[st+"stationCount"], stack="高速", label_opts=opts.LabelOpts(position="inside"))
        # 时间轴添加
        timelic.add(chart=bar, time_point="{0}时".format(i))

    timelic.render("t3.html")
    return timelic


def drawOneStBar(traindf: pandas.DataFrame, st: str) -> pyecharts.charts.Bar:

    xaxis = ["{0}时".format(i) for i in range(25)]  # x轴参数，时间
    bar = (
        pyecharts.charts.Bar(init_opts=opts.InitOpts(
            width="1000pt", height="500pt"))
        .add_xaxis(xaxis)
        .extend_axis(  # 额外的y轴，给折线使用
            yaxis=opts.AxisOpts(
                name="每小时车辆总数"
            )
        )  # 设置图表全局参数，如坐标轴名称
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name="时间",
                axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(
                name="各类型列车数",
                min_interval=2,  # 最小间隔设置为2
                axislabel_opts=opts.LabelOpts()),
            title_opts=opts.TitleOpts(title="{0}车站列车时间分布".format(st)),
            datazoom_opts=opts.DataZoomOpts(),)  # 可以按照x轴时间拖动
    )

    timdic = {"新空调快速": [], "新空调特快": [],
              "新空调直快": [], "动车": [], "高速": [], "城际": []}
    tot = []  # 用于记录每小时各种车的数量和总和
    for t in range(0, 25):
        ri = getStationProid(traindf, t)  # 按照车站来记录
        tot.append(sum(ri[st+"trainCount"]))  # zip来进行循环记录
        for tc, tt in zip(ri[st+"trainCount"], trainType):
            timdic[tt].append(tc)
    # 使用字典迭代来加入y轴数据
    for k, v in timdic.items():
        if len(k) > 3:  # 普速，设置stack来堆叠
            bar.add_yaxis(
                series_name=k, y_axis=v, stack="普速", label_opts=opts.LabelOpts(position="inside"))
        else:  # 高速
            bar.add_yaxis(series_name=k,
                          y_axis=v, stack="高速", label_opts=opts.LabelOpts(position="inside"))
    # 记录总和的折线，指定y轴为第二个，加入的额外y轴
    line = pyecharts.charts.Line().add_xaxis(
        xaxis).add_yaxis(series_name="每小时车次总数", y_axis=tot, yaxis_index=1)

    bar.overlap(line)  # 重叠
    bar.render("b2.html")
    return bar


def drawGantt(traindf: pandas.DataFrame, st: str):

    traindf["ent"] = [random.randint(0, 7) for i in range(0, len(traindf))]

    ganttCol = {"ent": "Task", "到时": "Start", "开时": "Finish"}
    gantDF = traindf.rename(columns=ganttCol)
    gantDF = gantDF[gantDF["停站"] == st]
    gantDF = gantDF.sort_values(by="Task", ascending=True)
    print(gantDF.head())
    fig = ff.create_gantt(df=gantDF, index_col="列车类型",
                          group_tasks=True, show_colorbar=True, show_hover_fill=True)
    fig.show()
    # fig.to_html("")
    return None


desired_caps = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '9',  # 手机安卓版本
    'deviceName': 'emulator-5554:5555',  # 设备名，安卓手机可以随意填写

    'appPackage': 'com.lltskb.lltskb',  # 启动APP Package名称
    'appActivity': '.ui.splash.SplashActivity',  # 启动Activity名称

    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App
    'newCommandTimeout': 6000,
    'automationName': 'UiAutomator2'
}


if __name__ == "__main__":

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.implicitly_wait(10)

    action = TouchAction(driver)  # 点选操作的对象
    TrainStationList(
        driver, action, ["G280", "G2664", "G466", "G2056"])

    # # 设置缺省等待时间
    time.sleep(3)
    driver.quit()
    # distrain = processStation("jnpart.txt")  # 济南Info.txt
    # drawGantt(distrain, "济南")

    #getStationProid(distrain, 6)
    # drawBarPieCount(distrain)
    # t1 = drawBarPie(distrain, 6)
    # t1.render("t2.html")
    #drawBarPie(distrain, 6).render("t2.html")
    # timeli = pyecharts.charts.Timeline()
    # for i in range(0, 25):
    #     timeli.add(drawBarPieSingle(distrain, i), "{0}时".format(i))
    # timeli.render("t3.html")
=======
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.android.nativekey import AndroidKey
from appium.webdriver.common.touch_action import TouchAction
import appium
from pyecharts import options as opts
from pyecharts.charts import Bar, Timeline
import random
import itertools
import pandas
import matplotlib
import pyecharts
import numpy
import time
import datetime
import plotly.figure_factory as ff
# 每一个车站的所有停车信息


def StationTrainList(driver: WebDriver, action: TouchAction, station: str):
    time.sleep(8)  # 等待开屏广告
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车站")')

    action.tap(stationText).perform()  # 点击车站选项的位置

    stationChk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/layout_station")  # 车站选择部分
    action.tap(stationChk).perform()  # 进入车站选择
    time.sleep(1)
    stationSelect = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/edit_input")  # 车站选择输入框
    stationSelect.send_keys(station)  # 输入

    stationFind = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("{0}")'.format(station))
    action.tap(stationFind[1]).perform()  # 输入车站名并确认，返回之前的页面

    searchbtn = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/querycz_btn")  # 搜索按钮
    action.tap(searchbtn).perform()  # 点选进行查找
    time.sleep(2)
    # 当前页面可视的车次部分
    pt = driver.find_element(AppiumBy.CLASS_NAME, 'android.widget.ListView')
    x1 = pt.size['width'] * 0.5
    y1 = pt.size['height']  # 获取页面宽高,方便后续滑动截取车次信息

    f = open(file="{0}Info.txt".format(station), mode="w", encoding="utf-8")
    # 设置为utf8，防止如复兴号，静音动车等符号导致报错
    settext = set()  # 使用set尽可能减少重复值

    while True:  # 滑动截取文字
        # 所有有文本的元素的集合，均为当前可见部分
        pageTrainList = driver.find_elements(
            AppiumBy.CLASS_NAME, 'android.widget.TextView')
        beforeSwipe = driver.page_source

        text = ""
        for i in range(0, len(pageTrainList)-9):  # 排除表头信息，仅保留车次部分
            text = text+pageTrainList[i+9].text+","  # 获取整体信息
            if (i+9) % 8 == 0:

                settext.add(text+"\n")
                text = ""

        try:
            # 这里模拟器的分辨率是1920*1080的手机屏幕
            # 如果内容少于一屏幕会直接报错，故使用try
            action.long_press(
                x=540, y=1800, duration=200).move_to(x=540, y=100).release()
            action.perform()  # 在中间滑动，选取新的车次信息
        # 如果滑动前后的元素相同，则表示已经到底了
        except Exception:  # 少于一屏幕就表示已经完成了
            break
        else:  # 前后的页面元素一样
            if driver.page_source == beforeSwipe:
                break
    for it in settext:
        f.write(it)            
    f.close()

    return

# 一组一列车的所有停站信息


def TrainStationList(driver: WebDriver, action: TouchAction, trainli: list[str]):
    time.sleep(8)  # 等待开屏广告
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车次")')
    action.tap(stationText).perform()  # 点击车次选项的位置

    stationchk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/chk_jpk")
    action.tap(stationchk).perform()  # 点选查找检票口选项
    # 设置为utf8，防止如复兴号，静音动车等符号导致报错
    f = open(file="{0}sInfo.txt".format(trainli[0]), mode="w", encoding="utf-8")
    settext = set()  # 使用set尽可能减少重复值
    for train in trainli:
        trainSelect = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/edit_train")
        trainSelect.clear()  # 清空内容防止重输
        trainSelect.send_keys(train)  # 输入查找车次

        searchbtn = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/querycc_btn")  # 搜索按钮
        action.tap(searchbtn).perform()  # 点选进行查找

        text = ""
        while True:  # 进入页面
            beforeSwipe = driver.page_source
# 当前页面上所有“查询”按钮，目前除了全部重复点一遍没有好办法
            searchbtns = driver.find_elements(
                AppiumBy.ID, "com.lltskb.lltskb:id/btn_query")  # 搜索按钮
            for btn in searchbtns:
                action.tap(btn).perform()  # 点选所有按钮进行查找
            pageStationList = driver.find_elements(
                AppiumBy.CLASS_NAME, 'android.widget.TextView')

           # 获取页面所有信息
            for i in range(1, len(pageStationList)):
                # 停站，到时，开时，检票口共四个停站信息
                text = text+pageStationList[i].text+","
                if i % 4 == 0:  # 每一个车站
                    text = train+","+text+"\n"

                    settext.add(text)
                    text = ""
            try:
                # 这里模拟器的分辨率是1920*1080的手机屏幕
                # 如果内容少于一屏幕会直接报错，故使用try
                action.long_press(
                    x=540, y=1800, duration=200).move_to(x=540, y=100).release()
                action.perform()  # 在中间滑动，选取新的车次信息
            # 如果滑动前后的元素相同，则表示已经到底了
            except Exception:  # 少于一屏幕就表示已经完成了
                break
            else:  # 前后的页面元素一样
                if driver.page_source == beforeSwipe:
                    break
        # 按下返回按键，进行下一次查找
        retbtn = driver.find_element(
            AppiumBy.ID, "com.lltskb.lltskb:id/btn_back")
        action.tap(retbtn).perform()
        # 替换两个汉字，方便后续操作
    for it in settext:
        it = it.replace("到", "").replace("开", "")
        f.write(it)
    f.close()

    return


def StationScreenList(driver: WebDriver, action: TouchAction, train: str):
    stationText = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("车站")')

    action.tap(stationText).perform()  # 点击车站选项的位置

    stationChk = driver.find_element(
        AppiumBy.ID, "com.lltskb.lltskb:id/btn_big_screen")  # 车站大屏选择
    action.tap(stationChk).perform()  # 车站大屏内容部分

    return


def processStation(fn: str)->pandas.DataFrame:

    # 读取文件，设置列名便于后续操作
    stationFrame = pandas.read_csv(filepath_or_buffer=fn,
                                   sep=",", encoding="utf-8")
    stationFrame.columns = ["车次", "drop1", "停站",
                            "到时", "开时", "始发站", "终到站", "列车类型", "drop2"]

    # 删去重复列和空列
    stationFrame.drop_duplicates(inplace=True)
    stationFrame.drop(columns=["drop1", "drop2"], inplace=True)
    stationFrame = dealTime(stationFrame)
    stationFrame["到时-小时"] = numpy.nan
    # print(stationFrame.head())

    for index, row in stationFrame.iterrows():
        stationFrame["到时-小时"][index] = row["到时"].hour

    return stationFrame


def dealTime(datafr: pandas.DataFrame, at="到时", lt="开时") -> pandas.DataFrame:
    # 对于始发车和终到车进行时间处理，默认相同
    for index, row in datafr.iterrows():
        if row[at] == "--:--":
            row[at] = row[lt]
        elif row[lt] == "--:--":
            row[lt] = row[at]

    # 计算停站时间
    datafr["到时"] = pandas.to_datetime(datafr["到时"])
    datafr["开时"] = pandas.to_datetime(datafr["开时"])
    datafr["停站时间"] = datafr["开时"]-datafr["到时"]
    # 实发终到设置停站时间
    # pd["停站时间"].replace(0,10,inplace=True)

    return datafr


trainType = ["新空调快速", "新空调特快", "新空调直快", "动车", "高速", "城际"]
stationRegion = ["济南", "济南西", "济南东", "大明湖"]

# 对于该车站群组（地区）时间段内的所有车次信息


def getStationProid(datafr: pandas.DataFrame, at: int) -> dict:
    # 预先分类
    datagruop = datafr.groupby(["到时-小时", "停站", "列车类型"])
    # print(datagruop.groups)
    regionInfo = {}

    # 对于每个车站的每种类型的列车
    for sr in stationRegion:
        # 好像只能分开写两层了
        regionInfo[sr+"trainCode"] = []
        regionInfo[sr+"trainCount"] = []
        for tt in trainType:
            try:  # 查找符合条件的群组
                i = datagruop.get_group((at, sr, tt))

            except KeyError:  # 索引找不到就是0
                regionInfo[sr+"trainCount"].append(0)
                # regionInfo["trainCode"].append(None)
            else:  # 如果没问题，添加回去长度

                regionInfo[sr+"trainCode"].append(i["车次"].tolist())
                regionInfo[sr+"trainCount"].append(len(i))
        regionInfo[sr+"trainCode"] = sum(regionInfo[sr+"trainCode"], [])
    # 解包嵌套的列表
    # print(regionInfo)

    return regionInfo


def getTrainProid(datafr: pandas.DataFrame, at: int) -> dict:
    # 预先分类
    datagruop = datafr.groupby(["到时-小时", "停站", "列车类型"])
    # print(datagruop.groups)
    regionInfo = {}

    # 对于每个车站的每种类型的列车
    for tt in trainType:
        # 好像只能分开写两层了
        regionInfo[tt+"trainCode"] = []
        regionInfo[tt+"stationName"] = []
        regionInfo[tt+"stationCount"] = []
        for st in stationRegion:
            try:  # 查找符合条件的群组
                i = datagruop.get_group((at, st, tt))

            except KeyError:  # 索引找不到就是0
                regionInfo[tt+"stationCount"].append(0)
                # regionInfo["trainCode"].append(None)
            else:  # 如果没问题，添加回去长度
                regionInfo[tt+"trainCode"].append(i["车次"].tolist())
                regionInfo[tt+"stationName"].append(i["停站"].tolist())
                regionInfo[tt+"stationCount"].append(len(i))

        regionInfo[tt+"stationName"] = sum(regionInfo[tt+"stationName"], [])
    # 解包嵌套的列表
    # print(regionInfo)

    return regionInfo


def drawBarPieSingle(traindf: pandas.DataFrame, seltime: int) -> pyecharts.charts.Bar:
    ri = getTrainProid(traindf, seltime)
    bar = (
        pyecharts.charts.Bar(init_opts=opts.InitOpts(
            width="1000pt", height="500pt"))
        .add_xaxis(stationRegion)  # 按照地区来获取
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(  # 倾斜名称，防止过场重叠
                axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(
                min_interval=2,  # 设置最小间距
                axislabel_opts=opts.LabelOpts()),
            title_opts=opts.TitleOpts(
                "济南地区停车数量 目前时间: {} 时".format(seltime)))
    )

    s1 = []  # 按照停站来统计列车数量
    for st in trainType:
        if len(st) > 3:  # 普速
            bar.add_yaxis(
                series_name=st, y_axis=ri[st+"stationCount"], stack="普速", label_opts=opts.LabelOpts(position="inside"))
        else:  # 高速
            bar.add_yaxis(series_name=st,
                          y_axis=ri[st+"stationCount"], stack="高速", label_opts=opts.LabelOpts(position="inside"))
        s1.append(ri[st+"stationName"])

    s2 = [len(i) for i in s1]  # 每一种列车的数量

    pie = (pyecharts.charts.Pie(init_opts=opts.InitOpts()
                                ).add(
        series_name="",  # 饼图参数，数据对为（列车类型，数量）
        data_pair=[list(z) for z in zip(trainType, s2)],
        radius=["10%", "30%"],
        center=["80%", "20%"],  # 设置大小和位置
        rosetype="radius",
        label_opts=opts.LabelOpts(is_show=True),
    )
    )
    # 重叠
    return bar.overlap(chart=pie)


def drawBarPieCount(traindf: pandas.DataFrame, ) -> pyecharts.charts.Timeline:
    timelic = pyecharts.charts.Timeline()
    totalTr = {}
    for i in range(0, 25):
        ri = getTrainProid(traindf, i)  # 按照车次来获取数据
        bar = (
            pyecharts.charts.Bar(init_opts=opts.InitOpts(
                width="1000pt", height="500pt"))
            .add_xaxis(stationRegion)  # 按照地区添加x轴

            .set_global_opts(  # 设置图表全局参数
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(
                    min_interval=2,
                    axislabel_opts=opts.LabelOpts()),
                title_opts=opts.TitleOpts(
                    title="济南地区停车数量 目前时间: {} 时".format(i)))
        )

        for st in trainType:  # 按照车辆类型分类
            if i == 0:
                totalTr[st+"stationCount"] = ri[st+"stationCount"]
            else:
                totalTr[st+"stationCount"] = [si+sj for si,
                                              sj in zip(totalTr[st+"stationCount"], ri[st+"stationCount"])]

            if len(st) > 3:  # 普速
                bar.add_yaxis(
                    series_name=st, y_axis=totalTr[st+"stationCount"], stack="普速", label_opts=opts.LabelOpts(position="inside"))
            else:  # 高速
                bar.add_yaxis(series_name=st,
                              y_axis=totalTr[st+"stationCount"], stack="高速", label_opts=opts.LabelOpts(position="inside"))
        # 时间轴添加
        timelic.add(chart=bar, time_point="{0}时".format(i))

    timelic.render("t3.html")
    return timelic


def drawOneStBar(traindf: pandas.DataFrame, st: str) -> pyecharts.charts.Bar:

    xaxis = ["{0}时".format(i) for i in range(25)]  # x轴参数，时间
    bar = (
        pyecharts.charts.Bar(init_opts=opts.InitOpts(
            width="1000pt", height="500pt"))
        .add_xaxis(xaxis)
        .extend_axis(  # 额外的y轴，给折线使用
            yaxis=opts.AxisOpts(
                name="每小时车辆总数"
            )
        )  # 设置图表全局参数，如坐标轴名称
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name="时间",
                axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(
                name="各类型列车数",
                min_interval=2,  # 最小间隔设置为2
                axislabel_opts=opts.LabelOpts()),
            title_opts=opts.TitleOpts(title="{0}车站列车时间分布".format(st)),
            datazoom_opts=opts.DataZoomOpts(),)  # 可以按照x轴时间拖动
    )

    timdic = {"新空调快速": [], "新空调特快": [],
              "新空调直快": [], "动车": [], "高速": [], "城际": []}
    tot = []  # 用于记录每小时各种车的数量和总和
    for t in range(0, 25):
        ri = getStationProid(traindf, t)  # 按照车站来记录
        tot.append(sum(ri[st+"trainCount"]))  # zip来进行循环记录
        for tc, tt in zip(ri[st+"trainCount"], trainType):
            timdic[tt].append(tc)
    # 使用字典迭代来加入y轴数据
    for k, v in timdic.items():
        if len(k) > 3:  # 普速，设置stack来堆叠
            bar.add_yaxis(
                series_name=k, y_axis=v, stack="普速", label_opts=opts.LabelOpts(position="inside"))
        else:  # 高速
            bar.add_yaxis(series_name=k,
                          y_axis=v, stack="高速", label_opts=opts.LabelOpts(position="inside"))
    # 记录总和的折线，指定y轴为第二个，加入的额外y轴
    line = pyecharts.charts.Line().add_xaxis(
        xaxis).add_yaxis(series_name="每小时车次总数", y_axis=tot, yaxis_index=1)

    bar.overlap(line)  # 重叠
    bar.render("b2.html")
    return bar


def drawGantt(traindf: pandas.DataFrame, st: str):

    traindf["ent"] = [random.randint(0, 7) for i in range(0, len(traindf))]

    ganttCol = {"ent": "Task", "到时": "Start", "开时": "Finish"}
    gantDF = traindf.rename(columns=ganttCol)
    gantDF = gantDF[gantDF["停站"] == st]
    gantDF = gantDF.sort_values(by="Task", ascending=True)
    print(gantDF.head())
    fig = ff.create_gantt(df=gantDF, index_col="列车类型",
                          group_tasks=True, show_colorbar=True, show_hover_fill=True)
    fig.show()
    # fig.to_html("")
    return None


desired_caps = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '9',  # 手机安卓版本
    'deviceName': 'emulator-5554:5555',  # 设备名，安卓手机可以随意填写

    'appPackage': 'com.lltskb.lltskb',  # 启动APP Package名称
    'appActivity': '.ui.splash.SplashActivity',  # 启动Activity名称

    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App
    'newCommandTimeout': 6000,
    'automationName': 'UiAutomator2'
}


if __name__ == "__main__":

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.implicitly_wait(10)

    action = TouchAction(driver)  # 点选操作的对象
    TrainStationList(
        driver, action, ["G280", "G2664", "G466", "G2056"])

    # # 设置缺省等待时间
    time.sleep(3)
    driver.quit()
    # distrain = processStation("jnpart.txt")  # 济南Info.txt
    # drawGantt(distrain, "济南")

    #getStationProid(distrain, 6)
    # drawBarPieCount(distrain)
    # t1 = drawBarPie(distrain, 6)
    # t1.render("t2.html")
    #drawBarPie(distrain, 6).render("t2.html")
    # timeli = pyecharts.charts.Timeline()
    # for i in range(0, 25):
    #     timeli.add(drawBarPieSingle(distrain, i), "{0}时".format(i))
    # timeli.render("t3.html")
>>>>>>> df47c64 (初始提交)

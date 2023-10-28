import pandas
import random
import os


def getArrLeaSt(station, stype):

    stcode = ""
    # 多路径车站部分
    if stype == "高速":  # 高速
        ArrLeaveSt = {
            '汉口': '沪蓉线汉口方向',
            '宜昌东': '沪蓉线汉口方向',
            '襄阳东': '沪蓉线汉口方向',
            '成都东': '沪蓉线汉口方向',
            '利川': '沪蓉线汉口方向',
            '重庆北': '沪蓉线汉口方向',
        }
    else:  # 动车城际speedType == "动车" or speedType == "城际"
        ArrLeaveSt = {
            '汉口': '丹水池联络线汉口方向',
            '宜昌东': '丹水池联络线汉口方向',
            '襄阳东': '丹水池联络线汉口方向',
            '成都东': '丹水池联络线汉口方向',
            '利川': '丹水池联络线汉口方向',
            '重庆北': '丹水池联络线汉口方向',
        }

    stcode = ArrLeaveSt.get(station)
    if stcode != None:
        # print("车次:{0} 车站:{1} ".format(type, station))
        return stcode

    # 常规单路径车站
    ArrLeaveSt = {
        '武汉': '武汉动车所',
        '南宁东': '京广高速咸宁北方向',
        '北京西': '京广高速孝感北方向',
        '南昌西': '武九客专葛店南方向',
        '香港西九龙': '京广高速咸宁北方向',
        '广州南': '京广高速咸宁北方向',

        '深圳北': '武九客专葛店南方向',
        '西安北': '京广高速孝感北方向',
        '温州南': '武九客专葛店南方向',
        '兰州西': '京广高速孝感北方向',
        '长沙南': '京广高速咸宁北方向',
        '郑州东': '京广高速孝感北方向',
        '贵阳北': '京广高速咸宁北方向',
        '昆明南': '京广高速咸宁北方向',
        '上海虹桥': '沪蓉线红安西方向',
        '合肥东': '沪蓉线红安西方向',
        '厦门': '武九客专葛店南方向',
        '南京南': '沪蓉线红安西方向',
        '福州': '武九客专葛店南方向',
        '杭州东': '武九客专葛店南方向',
        '南昌': '武九客专葛店南方向',
        '济南': '京广高速孝感北方向',
        '青岛北': '京广高速孝感北方向',
        '沈阳北': '京广高速孝感北方向',
        '厦门北': '武九客专葛店南方向',
        '大冶北': '武九客专葛店南方向',
        '福州南': '武九客专葛店南方向',
        '黄冈东': '武九客专葛店南方向',
        '安庆': '武九客专葛店南方向',
    }
    stcode = ArrLeaveSt.get(station, "")
    if stcode == "":
        print(f"车站:{station} 未找到")
    return stcode


def checkin(entrance: str) -> int:
    # 终到车等不指定
    if entrance == "":
        return 0
    # 检票口A5 非终到车
    try:
        en = entrance[-1]
    except TypeError:
        return 0

    railrange = [0, 0]
    if en == '1':  # 高速场
        railrange = [1]
    elif en == '2':
        railrange = [2, 3, 4]
    elif en == '3':
        railrange = [5, 6, 7]
    elif en == '4':  # 78道对应京广高速正线
        railrange = [8, 9, 10]
    elif en == '5':
        railrange = [11, 12, 13]
    elif en == '6':
        railrange = [14, 15, 16]  # 存在分界
    elif en == '7':  # 综合场
        railrange = [17, 18, 19]
    else:
        railrange = [20]
    return random.choice(railrange)


def routedispatch(stoptruck: int, routearr: str) -> str:
    # 对于分场式车站按线路所分流进场车辆
    if stoptruck >= 1 and stoptruck <= 14:  # 高速场车辆
        k1 = {"武九客专葛店南方向": "武汉南线路所2",
              "沪蓉线汉口方向": "湛家矶线路所1",
              "丹水池联络线汉口方向": "湛家矶线路所1"}
    else:  # 综合场车辆
        k1 = {
            "武九客专葛店南方向": "武汉南线路所1",
            "沪蓉线汉口方向": "湛家矶线路所2",
            "丹水池联络线汉口方向": "湛家矶线路所2"}

    return k1.get(routearr, "")


# s1 = ("武九客专葛店南方向", "高速场")
# k1.get(s1)


whhd = pandas.read_csv(filepath_or_buffer="武汉v2.1\\wh1test.csv", sep=",",header=0)
whhd.fillna("",inplace=True)

whhd["ent"] = whhd["检票口"].apply(lambda x: checkin(x))
whhd["arr"] = whhd.apply(lambda x: getArrLeaSt(x["始发站"], x["类型"]),axis=1) 
whhd["lea"] = whhd.apply(lambda x: getArrLeaSt(x["终到站"], x["类型"]),axis=1)
whhd["前后站"]=whhd.apply(lambda x : [x["arr"], x["lea"]],axis=1)

whhd["arrtru"] = whhd.apply(
    lambda x: routedispatch(x["ent"], x["arr"]), axis=1)
print(whhd)

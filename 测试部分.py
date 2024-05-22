import requests
import json
import random
import time
import datetime
import pandas

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


src = (1, 2, 3, 4)
sre1 = {1, 2, 3, 4}

route12 = {
    "野三关": ["沪蓉线恩施方向", "宜昌西线路所"], "高坪": ["沪蓉线恩施方向", "宜昌西线路所"],
    "建施": ["沪蓉线恩施方向", "宜昌西线路所"], "恩施": ["沪蓉线恩施方向", "宜昌西线路所"], "利川": ["沪蓉线恩施方向", "宜昌西线路所"],
    "石柱县": ["沪蓉线恩施方向", "宜昌西线路所"], "丰都": ["沪蓉线恩施方向", "宜昌西线路所"],
    "长寿北": ["沪蓉线恩施方向", "宜昌西线路所"], "重庆北": ["沪蓉线恩施方向", "宜昌西线路所"],

    "枝江北": ["沪蓉线荆州方向", "宜昌东线路所"], "荆州": ["沪蓉线荆州方向", "宜昌东线路所"],
    "潜江": ["沪蓉线荆州方向", "宜昌东线路所"], "天门南": ["沪蓉线荆州方向", "宜昌东线路所"], "仙桃西": ["沪蓉线荆州方向", "宜昌东线路所"],
    "汉川": ["沪蓉线荆州方向", "宜昌东线路所"], "汉口": ["沪蓉线荆州方向", "宜昌东线路所"], "武昌": ["沪蓉线荆州方向", "宜昌东线路所"],

    "枝城": ["焦柳线松滋方向", "新昌站"], "松滋": ["焦柳线松滋方向", "新昌站"],
    "张家界": ["焦柳线松滋方向", "新昌站"], "石门县北": ["焦柳线松滋方向", "新昌站"],

    "荆门": ["焦柳线荆门方向", "鸦雀岭站", "新昌站"], "宜城": ["焦柳线荆门方向", "鸦雀岭站", "新昌站"], "襄阳": ["焦柳线荆门方向", "鸦雀岭站", "新昌站"],

    "宜昌东客整所,动车所": ["宜昌东站"],
}


def randomplatform(a, b) -> int:
    return random.randint(a, b)


entrance12 = {
    ("沪蓉线恩施方向", "宜昌西线路所", "宜昌东站", "宜昌东线路所", "沪蓉线荆州方向"): (1, 2, (5, 9), 2, 1),
    ("沪蓉线荆州方向", "宜昌东线路所", "宜昌东站", "宜昌西线路所", "沪蓉线恩施方向"): (2, 3, (5, 9), 3, 2),

    ("沪蓉线恩施方向", "宜昌西线路所", "宜昌东站", "新昌站", "鸦雀岭站", "焦柳线荆门方向"): (1, 2, (6, 9), 1, 4, 2),
    ("焦柳线荆门方向", "鸦雀岭站", "新昌站", "宜昌东站", "沪蓉线恩施方向", "宜昌西线路所"): (1, 4, 1, (2, 5), 3, 2),

    ("宜昌东客整所,动车所", "宜昌东站", "宜昌东线路所", "沪蓉线荆州方向"): (1, (6, 9), 2, 1),
    ("宜昌东客整所,动车所", "宜昌东站", "宜昌西线路所", "沪蓉线恩施方向"): [2, (1, 5), 3, 2],

}

# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
gameStationInfo = {'武昌': ['a', -1, 0, 0, 0], '汉西联络线至新墩': ['c', 1, 1, 2, 8],
                   '京广线汉口': ['b', 0, 1, 2, 8], '京广线咸宁': ['d', 0, 2, 1, 7],
                   '武咸城际南湖东': ['e', 0, 2, 1, 4], '南环线何流': ['f', 0, 2, 1, 8], '武客技': ['g', -1, 0, 0, 20]}
gameStationDefault = ['g', -1, 0, 0, 20]  # 找不到的默认设置
# 线路和车站关系，主要用于从车站-值获取线路-键
route1 = {"汉西联络线": ["应城", "天门", "京山", "钟祥", "云梦", "安陆", "随州", "枣阳", "襄阳", "汉川", "天门南", "仙桃", "仙桃西", "潜江"],
          '京广线汉口方向': ["郑州", "许昌", "信阳", "漯河", "驻马店", "长葛", "花园", "孝感", "广水", "麻城"],
          '京广线咸宁方向': ["咸宁", "赤壁", "临湘", "岳阳", "长沙", "广州", "广州东", "深圳"],
          '武咸城际南湖东方向': ["南湖东", "武汉东", "葛店南", "庙山", "纸坊东", "汤逊湖"],
          '南环线何流方向': ["鄂州", "黄石", "阳新" "大冶", "南昌"],
          "汉口汉西联络线至汉口站": ["汉口",],
          '武客技': ["武昌"]}
route2 = {}
for k, v in route1.items():
    for l in v:
        route2[l] = k


route12 = {'应城': ['汉西联络线', "汉西站", "汉阳站"], '天门': ['汉西联络线', "汉西站", "汉阳站"],
           '京山': ['汉西联络线', "汉西站", "汉阳站"], '钟祥': ['汉西联络线', "汉西站", "汉阳站"], '云梦': ['汉西联络线', "汉西站", "汉阳站"],
           '安陆': ['汉西联络线', "汉西站", "汉阳站"], '随州': ['汉西联络线', "汉西站", "汉阳站"],
           '枣阳': ['汉西联络线', "汉西站", "汉阳站"], '襄阳': ['汉西联络线', "汉西站", "汉阳站"], '汉川': ['汉西联络线', "汉西站", "汉阳站"], '天门南': ['汉西联络线', "汉西站", "汉阳站"], '仙桃': ['汉西联络线', "汉西站", "汉阳站"], '仙桃西': ['汉西联络线', "汉西站", "汉阳站"], '潜江': ['汉西联络线', "汉西站", "汉阳站"],

           '郑州': ['京广线汉口方向', "汉西站", "汉阳站"], '许昌': ['京广线汉口方向', "汉西站", "汉阳站"], '信阳': ['京广线汉口方向', "汉西站", "汉阳站"], '漯河': ['京广线汉口方向', "汉西站", "汉阳站"],
           '驻马店': ['京广线汉口方向', "汉西站", "汉阳站"], '长葛': ['京广线汉口方向', "汉西站", "汉阳站"], '花园': ['京广线汉口方向', "汉西站", "汉阳站"], '孝感': ['京广线汉口方向', "汉西站", "汉阳站"], '广水': ['京广线汉口方向', "汉西站", "汉阳站"], '麻城': ['京广线汉口方向', "汉西站", "汉阳站"],

           '咸宁': ['京广线咸宁方向', "余家湾站"], '赤壁': ['京广线咸宁方向', "余家湾站"], '临湘': ['京广线咸宁方向', "余家湾站"], '岳阳': ['京广线咸宁方向', "余家湾站"], '长沙': ['京广线咸宁方向', "余家湾站"],
           '广州': ['京广线咸宁方向', "余家湾站"], '广州东': ['京广线咸宁方向', "余家湾站"], '深圳': ['京广线咸宁方向', "余家湾站"],

           '南湖东': ['武咸城际南湖东方向', "余家湾站"], '武汉东': ['武咸城际南湖东方向', "余家湾站"], '葛店南': ['武咸城际南湖东方向', "余家湾站"],
           '庙山': ['武咸城际南湖东方向', "余家湾站"], '纸坊东': ['武咸城际南湖东方向', "余家湾站"], '汤逊湖': ['武咸城际南湖东方向', "余家湾站"],

           '鄂州': ['武昌南环线何流方向', "余家湾站"], '黄石': ['武昌南环线何流方向', "余家湾站"], '阳新大冶': ['武昌南环线何流方向', "余家湾站"], '南昌': ['武昌南环线何流方向', "余家湾站"],
           '汉口': ['汉口汉西联络线至汉口站', "汉西站", "汉阳站"], '武昌': ['武客技']}

# c = 沪蓉线红安西方向 | 1 | 1, 2
# a = 汉口站 | 1 | 12, 16, 18, 15, 4, 5, 3, 2, 1, 11, 7, 8, 14, 13, 17, 10, 9, 6
# b = 沪蓉线汉川方向 | 1 | 1, 2
# d = 汉口动车所 | 1 | 1, 2
# e = 丹水池联络线武汉方向 | 1 | 2, 1
# f = 京广线武昌方向 | 1 | 1, 2
# g = 京广线孝感方向 | 1 | 1, 2
# h = 汉丹线应城襄阳方向 | 1 | 1, 2
# i = 汉孝城际天河机场方向 | 1 | 1, 2
# j = 京广高速孝感北方向 | 1 | 2, 1
# k = 京广高速武汉方向 | 1 | 1, 2
# l = 丹水池 | 1 |
# m = 横店东 | 1 |

s0 = "D2271/D2274 COMMUTER 250 LLPPPPLL X1 : b#2#14:51:00#0 a#15#14:55:00#14 c#2#15:12:00#0"
hsShiyan = ["汉十高速十堰东方向"]
hsHankou = ["汉十高速汉口方向"]
zyShennongjia = ["郑渝高速神农架方向", "东津线路所"]
zyZhengzhou = ["郑渝高速郑州东方向"]

# 综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entrance12 = {
    (*hsHankou, "襄阳东", *hsShiyan[::-1]): [1, (6, 8), 1],
    (*hsHankou, "襄阳东", *zyZhengzhou[::-1]): [1, (9, 10), 2],
    (*hsHankou, "襄阳东", *zyShennongjia[::-1]): [1, (6, 8), 5, 1],
    (*hsHankou, "襄阳东", "动车所"): [1, (6, 8), 0],


    (*hsShiyan, "襄阳东", *hsHankou[::-1]): [2, (1, 3), 2],
    (*hsShiyan, "襄阳东", *zyZhengzhou[::-1]): [2, (9, 9), 2],

    (*zyZhengzhou, "襄阳东", *hsShiyan[::-1]): [1, (9, 9), 1],
    (*zyZhengzhou, "襄阳东", *hsHankou[::-1]): [1, (9, 10), 2],
    (*zyZhengzhou, "襄阳东", *zyShennongjia[::-1]): [1, (14, 20), 4, 1],
    (*zyZhengzhou, "襄阳东", "动车所"): [1, (14, 20), 0],

    (*zyShennongjia, "襄阳东", *zyZhengzhou[::-1]): [2, 3, (10, 11), 1],
    (*zyShennongjia, "襄阳东", *hsHankou[::-1]): [2, 2, (1, 3), 2],
    (*zyShennongjia, "襄阳东",   "动车所"): [2, 3, (14, 20), 0],

    ("动车所", "襄阳东", *zyShennongjia[::-1]): [3, (14, 20), 4, 1],
    ("动车所", "襄阳东", *zyZhengzhou[::-1]): [2, (14, 20), 2],
    ("动车所", "襄阳东", *hsShiyan[::-1]): [1, (1, 3), 1],
    ("动车所", "襄阳东", *hsHankou[::-1]): [2, (6, 8), 2],


}
InfoListList=[['D2195/D2198', '汉口', '06:43', '06:43', '0', '0'], ['D2195/D2198', '红安西', '07:12', '07:14', '72', '0'], ['D2195/D2198', '麻城北', '07:28', '07:30', '111', '0'], ['D2195/D2198', '金寨', '08:03', '08:05', '220', '0'], ['D2195/D2198', '六安', '08:22', '08:24', '272', '0'], ['D2195/D2198', '合肥南', '08:50', '08:54', '359', '0'], ['D2195/D2198', '南京南', '09:46', '09:50', '516', '0'], ['D2195/D2198', '宜兴', '10:28', '10:31', '645', '0'], ['D2195/D2198', '杭州东', '11:11', '11:15', '772', '0'], ['D2195/D2198', '余姚北', '11:49', '11:51', '878', '0'], ['D2195/D2198', '宁波', '12:15', '12:15', '92', '0']]
routeList = {"station": ["武汉","汉口","红安西","麻城北","合肥南","合肥", ],
             "way": [ "0", "0","1", "1","2", "2"],}

 # 区间内所有车站名称
sectionst = pandas.DataFrame(
    data=routeList, columns=["station", "way"])
print(sectionst)

# 单一车次
trainst = pandas.DataFrame(data=InfoListList, columns=[
    "traincode", "station", "arrival", "departure", "entrance", "drop0"])
trainst.drop(columns="drop0", inplace=True)
print(trainst)

# 合并二者
sectionTrain = pandas.merge(
    left=sectionst, right=trainst, how="inner", on=["station"], suffixes=("", ""))
print(sectionTrain)


'''
# 线路和车站关系，主要用于从车站-值获取线路-键
route12 = {"潢川": ["京九线阜阳方向"], "光山": ["京九线阜阳方向"], "阜阳": ["京九线阜阳方向"], "商丘南": ["京九线阜阳方向"], "商丘": ["京九线阜阳方向"],
           "新县": ["京九线阜阳方向"],
           "黄州": ["京九线九江方向"], "武穴": ["京九线九江方向"], "九江": ["京九线九江方向"], "庐山": ["京九线九江方向"], "南昌": ["京九线九江方向"],
           "蕲春": ["京九线九江方向"], "赣州": ["京九线九江方向"], "浠水": ["京九线九江方向"], "吉安": ["京九线九江方向"],
           "武昌": ["麻武线武昌方向"], "信阳": ["麻武线武昌方向"],
           '麻城': ['麻城站货场']}

route1Default = ["麻城站货场"]  # 找不到的默认设置

# 综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entrance12 = {
    ("京九线阜阳方向", "麻城", "京九线九江方向"): [1, (1, 3), 1],
    ("京九线阜阳方向", "麻城", "麻武线武昌方向"): [1, (1, 3), 1],


    ("京九线九江方向", "麻城", "京九线阜阳方向"): [2, (4, 5), 2],
    ("京九线九江方向", "麻城", "麻武线武昌方向"): [2, (4, 5), 1],

    ("麻武线武昌方向", "麻城", "京九线阜阳方向"): [1, (4, 5), 2],
    ("麻武线武昌方向", "麻城", "京九线九江方向"): [1, (1, 3), 1],

    ("京九线九江方向", "麻城", "麻城"): [1, (1, 1), 1],


}
# a = 襄阳东站 | 1 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 
# b = 汉十高速丹江口十堰东方向 | 1 | 1, 2 
# c = 汉十高速孝感东汉口方向 | 1 | 1, 2 
# d = 郑渝高速南阳东郑州东方向 | 1 | 1, 2 
# e = 郑渝高速神农架重庆北方向 | 1 | 1, 2 
# f = 襄阳东动车所 | 1 | 1, 2, 3 
# g = 襄荆高速荆门东荆州方向(在建) | 1 | 1, 2 
# h = 东津线路所 | 1 | 1, 2, 3, 4, 5, 6 
221|221 COMMUTER 120 LPPPL X1 : c#0#08:00:00#0 a#9#08:05:00#1 d#0#08:11:00#0
537|537 COMMUTER 120 LPPPL X1 : e#0#08:00:00#0 h#2#08:02:00#0 f#1#08:07:00#1 a#0#08:13:00#0
611|611 COMMUTER 120 LPPPL X1 : d#1#08:00:00#0 a#14#08:05:00#1 h#4#08:10:00#0 e#1#08:12:00#0
620|620 COMMUTER 120 LPPPL X1 : b#2#08:00:00#0 a#3#08:05:00#1 c#2#08:11:00#0

'''

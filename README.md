# 大标题
## 圣遗物
整体上古早时期的方案流程基本不变，各种早期内容都在对应文件夹的notebook里  
1. 目前基于信息源（**路路通pc程序**）主要使用多级映射生成时刻表
2. 对于其他信息源也有早期预留的接口，但是由于方法问题暂时没有采用
   - 对于web段12306使用selenium获取相应信息
   - 对于移动端使用appnium进行自动化
   - 对于已有表格信息源有其他处理方式
3. 分别整理车辆信息和时刻表信息文本合并输出结果  

## 当前状态  

数据源信息对比  

| 爬取方法     | 数据源            | 优点                                 | 缺点                                        |
| ------------ | ----------------- | ------------------------------------ | ------------------------------------------- |
| uiautomation | pc端路路通程序    | 速度快较为准确，获取结果确定         | 难以使用多线程优化速度                      |
| selenium     | 12306             | 查询快捷且在线数据时效性好           | 车次需要预先获取，信息量太少且需要验证      |
| appnium      | 相应移动端程序    | 各种信息均较为全面，支持按照车站查找 | appnium配置复杂且本身不太稳定，查询自动化慢 |
| 无--手动     | excel等格式化数据 | 数据本身灵活性较高                   | 获取excel数据本身较慢                       |

### 早期运用方法
1. 数据获取部分，有selenium和appnium两种均为爬取自动化，也可以是表格等信息
    1.1 selenium通过爬取12306可以获得较为详细的<b>单个车次</b> 信息，但是12306本身信息较少  
    1.2 appnium通过爬取路路通安卓APP来获得整体上更详细的信息，但是appnium本身已经不在维护  
    1.3 也可以通过其他方式如excel等预先获得的数据省去爬取直接进行后续处理
2. 数据处理部分，使用偏函数式编程来抽出处理函数配合pandas库来处理数据，整体上分为3部分  
    2.1 读取爬取的信息进行数据清洗和数据类型转换如date类型  
    2.2 计算处理得到游戏时刻表需要的数据如进路映射    
    2.3 生成时刻表样式的字符串并写入文件

### 当前运用方法
1. 至v3版本改用uiautomation和pc端路路通程序来进行自动化获取数据
   - uiautomation获取数据相对较快，且数据获取过程直观更便于处理
   - 路路通程序为mfc应用，自动化较为便捷
2. 使用生产者消费者模式分开获取数据和处理数据
   - 生产者作为一个对象获取原生数据（复制），传输到队列中
   - 消费者从队列获取数据，通过函数来处理数据
3. 数据处理部分修改为流处理
   - 不断从队列获取数据，每次仅处理一个车次
   - 本身程序大量时间在等待io，流处理损失时间并不多
4. 重整最终结果来手动修改部分暂未实现的功能
    - 手动合并立折车次
    - 对于没有考虑到的时刻表手动改正


## 概况  
大体上仍然是数据获取和数据处理两部分，数据处理部分又结合两种不同爬取方式修改合并在notebook中  
当前使用生产者-消费者模型来优化程序逻辑，暂未整理为notebook仍为py程序
### uiautomation版
**详见武汉枢纽v3以及之后的版本**
uiautomation自动化从路路通pc端程序获取数据，自动化单一车站，主要信息为路路通pc端程序中单一车次的所有信息，由于在24年年初数据库改动离线数据没有检票口数据，虽然预留有接口但是没有使用的地方了，但是目前可以根据游戏地图本身信息使用多级映射来完善进路信息。数据处理部分则基本不变，主要从之前的批处理改为流处理。
预留有自动化区间的接口，但是尚未完善

### appnium版--不更新弃用  
**详见济南西2.0版本处**
appnium自动化和对应的数据处理，包含对于路路通移动端APP中车站查询和车次检票口查询两个自动化爬取，以及后续数据处理。两个爬取理论上为先爬取车站信息，之后如果不需要做检票口/进路精确映射可以直接使用获取车站信息来生成字符串（未加入，实现为检票口填充0），如需要映射则将车站车次做车次检票口爬取获得详细时刻表和路径信息。完成后可生成游戏时刻表  

### selenium版  
**详见武汉2.1版本及以前版本**
selenium自动化和对应的数据处理，包含对于12306web中交路表和检票口查询两个自动化爬取，以及后续数据处理。两个查询均只能针对单一车次进行，需要预先获取查询计划的所有车次来进行多轮查询，但是由于是web爬取本身速度较快而且网络稳定则基本不会中断。理论上两个爬取要一起使用以分别获取交路表和检票口，爬取生成两个文件会在第一步处理时进行合并，后续处理步骤基本相同  
目前查询会获取本车次的所有停站信息导致数据量偏大，实际上只需要目标站前后站的数据，后续考虑在获取表格数据时就加入筛选  

### 表格版
**单独的数据处理部分，分离较为明显的部分可见武汉2.1**
基于表格数据来生成相应的时刻表数据，当然这种文件内容丰富程度丰俭由人，这里的就相对比较少，仅有 始发/终到、到时/开时 和可能不存在的检票口信息，一共四种或是五中信息，本身是上面两个带爬取的数据处理部分经过部分修改。


### 数据处理部分   
单独抽出的数据处理部分，如时间处理等，大量使用映射和apply函数(lambda表达式)方法来提高复用性(虽然基本没有复用的)和可读性(虽然也不读吧),主要为pandas库等处理  
因为仅为单纯抽出为函数并没有实际上的意义导致耦合较高但是修改相对容易  
如果要使用基本只需要修改映射关系以及主函数部分少数参数
以当前麻城站为例部分映射如下  
```python
# 速度和编组以及类型映射关系,0为普速1为动车2为高速，后续修改
species1 = {'K': ['120', 'LCPPPPPPPP', "0"], 'T': ['140', 'LCPPPPPPPP', "0"]}
# [车站编号,车站所在侧(0为左侧),车辆进场股道,车辆离场行走股道,到达中心车站所用时间]
# 对于股道，若为边界进出场车站股道为进场立场行走股道编号，若为越行站则为对应正线、越行线编号
gameStationInfo = {'麻城': ['a', 0, 0, 0],'京九线阜阳方向': ['b', 1, 2, 6], '京九线九江方向': ['c', 2, 1, 6],}
# 线路和车站关系，主要用于从车站-值获取线路-键
route12 = {"潢川": ["京九线阜阳方向"], "光山": ["京九线阜阳方向"], "阜阳": ["京九线阜阳方向"], }
# 综和可能的进路，产生股道，做较为准确的映射,主要车站的tuple是随机映射站台用的
entrance12 = {("京九线阜阳方向", "麻城", "京九线九江方向"): [1, (1, 3), 1],}
```  
  
### 主函数部分
程序运行的主函数，如需使用进需要修改相关常量，如车站名称，停车数量，以及路路通pc程序的路径等
```python
if __name__ == "__main__":
    InfoQueue1 = multiprocessing.Queue()  # 径路信息队列
    trainCodeQueue1 = multiprocessing.Queue()  # 车次号队列
    # 中继承接队列
    targetstation = "麻城"
    lltskbroute = "lltskb\\lltskb.exe"

    # 生产者进程，中间的75为当前车站车次总数，约数即可
    p = multiprocessing.Process(
        target=obtaintrain, args=(lltskbroute, 75, targetstation, InfoQueue1, trainCodeQueue1,))
    # 消费者进程
    c = multiprocessing.Process(
        target=gameStrProcess, args=(targetstation, InfoQueue1, trainCodeQueue1, "text2.txt"))

    p.start()  # 启动生产者和消费者进程
    time.sleep(10)  # 启动较慢，等待生产者初始化完成
    c.start()

    p.join()  # 等待生产者进程完成
    InfoQueue1.put("114514")  # magic number,通知消费者所有产品已经生产完毕
    c.join()  # 等待消费者进程完成

    strReproduct("text2.txt", "麻城.txt")  # 重整结果便于合并立折车次
```

## 改进信息
*自3.0版本后*
1. 武汉枢纽车站v3.0
- 采用uiautomation和路路通pc端程序获取数据
- 处理方式改为流处理，便于后期使用区间数据
- 程序改用mutliprocess多进程库建立生产者-消费者模型，改善程序表现
2. 宜昌襄阳v3.1
- 加入多级映射完善进路，更好的支持 核心车站--中间线路所、车站--进场立场线路 三级组织架构
- 整合映射函数，分流为线路映射，车站映射等，合并原先过于稀碎的映射函数
3. 麻城站v3.2
- 修改了部分处理函数，改善可读性并为后续加入多停站区间处理预留接口
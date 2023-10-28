# 大标题
## 圣遗物
整体上古早时期的方案如葛店南和汉口等大体方向正确，内容都在notebook里  
1. 葛店南/鄂州等小站检票口和股道信息缺乏映射或完全缺失--按照上下行/优先度等映射
2. 汉口等无离线/固定映射关系--采用车站大屏/即时查询等时效性较高的方式
3. 武汉等一检票口对多站台映射--后续如果有冲突在修改  
4. 济南西等严格固定的车站--注意爬取准确性  

## 当前状态  
1. 数据获取部分，有selenium和appnium两种均为爬取自动化，也可以是表格等信息
    1.1 selenium通过爬取12306可以获得较为详细的<b>单个车次</b> 信息，但是12306本身信息较少  
    1.2 appnium通过爬取路路通安卓APP来获得整体上更详细的信息，但是appnium本身已经不在维护  
    1.3 也可以通过其他方式如excel等预先获得的数据省去爬取直接进行后续处理
2. 数据处理部分，使用偏函数式编程来抽出处理函数配合pandas库来处理数据，整体上分为3部分  
    2.1 读取爬取的信息进行数据清洗和数据类型转换如date类型  
    2.2 计算处理得到游戏时刻表需要的数据如进路映射    
    2.3 生成时刻表样式的字符串并写入文件
3. 数据源信息对比  

数据源|优点|缺点  
---|---|---   
selenium爬取|查询快捷且当天数据时效性好|车次需要预先获取，信息量太少后续需寻找新的数据源     
appnium爬取|各种信息均较为全面，支持按照车站查找 |appnium配置复杂且本身不太稳定，查询自动化慢    
excel等格式化数据| 数据本身灵活性较高 |获取excel数据本身较慢  

## 概况  
大体上仍然是数据获取和数据处理两部分，数据处理部分又结合两种不同爬取方式修改合并在notebook中  
### 济南西站appnium版  
appnium自动化和对应的数据处理，包含对于路路通APP中车站查询和车次检票口查询两个自动化爬取，以及后续数据处理。两个爬取理论上为先爬取车站信息，之后如果不需要做检票口/进路精确映射可以直接使用获取车站信息来生成字符串（未加入，实现为检票口填充0），如需要映射则将车站车次做车次检票口爬取获得详细时刻表和路径信息。完成后可生成游戏时刻表  

### 济南西站appnium版  
selenium自动化和对应的数据处理，包含对于12306web中交路表和检票口查询两个自动化爬取，以及后续数据处理。两个查询均只能针对单一车次进行，需要预先获取查询计划的所有车次来进行多轮查询，但是由于是web爬取本身速度较快而且网络稳定则基本不会中断。理论上两个爬取要一起使用以分别获取交路表和检票口，爬取生成两个文件会在第一步处理时进行合并，后续处理步骤基本相同  

### 武汉站表格版
基于表格数据来生成相应的时刻表数据，当然这种文件内容丰富程度丰俭由人，这里的就相对比较少，仅有 始发/终到、到时/开时 和可能不存在的检票口信息，一共四种或是五中信息，本身是上面两个带爬取的数据处理部分经过部分修改。


### 数据处理部分   
单独抽出的数据处理部分，如时间处理等，大量使用函数和apply(lambda)方法来提高复用性和可读性(虽然没人读吧),主要为pandas库等处理  

## 改进
1. 对于线路所-分场式车站进行固定进路映射
2. 寻找如车站大屏等更为全面的信息完善获取部分
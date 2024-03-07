import random

#point类只单独存储结点个数，结点的边的信息单独存储，节约存储空间，而且访问效率高
#point类只用于单独定义一个存储maxVertexNum个结点的数组，用于存储且查询顶点的相关信息
#存储边的信息使用一个二维数组存储
class pointC:       #存储单个结点的详细信息
    isColored = 0   #是否着色
    color = 0       #颜色号
    # num = 0       #结点号,不需要，下标即是结点号

maxVertexNum = 0 #最大顶点数
maxEdgeNum = 0 #最大边数

edge = []   #edge存储边的相连信息，即邻接矩阵
point = [] #points存储顶点的相关信息
# color = [] #colors存储使用了的颜色信息
nextNeighbor = []   #存储结点的邻居结点
nextNextNeighbor = []   #存储结点的邻居的邻居结点，不能包括自身结点
nnnNeighbor = [] #邻居结点和邻居的邻居结点的并集（不包括自身结点）
nnnColorList = []  #所有邻居结点和邻居的邻居结点的颜色集合
fites = [] #存储种群的适应度
# totalSetList = {} #这种定义方式指的是字典类型
totalSetList = set()
foundMinColorNum = 999999
foundMinPointSeq = []

def readGraph(filename):
    # 打开文件
    # files = ['','circle-3.txt','circle-4.txt','1-FullIns_3.wsc']
    # f = open(files[2],'r')
    f = open(filename,'r')
    # f = open('circle-3.txt','r')
    temp = f.readline().split(' ')
    global maxVertexNum
    global maxEdgeNum

    #图文件第一行标注的是所有顶点数和所有边数
    #注意：顶点数是确实正确的顶点数，且边数也是真正的边数，
    #     但是后面给出的边的端点坐标只会出现一次，不会出现倒序再来一次的情况。
    maxVertexNum = int(temp[0])
    maxEdgeNum = int(temp[1])

    #初始化图结构

    l = [0] * maxVertexNum
    for i in range(maxVertexNum):
        edge.append(l.copy())
    #读取文件，重构图的边为二维数组
    for i in range(maxEdgeNum):
        temp = f.readline().split(' ')
        r = int(temp[0])
        l = int(temp[1])
        edge[r][l] = 1  #没有标注对角线元素的边，即默认是0
        # edge[l][r] = 1  #因为只标注一次边的端点信息，所以我们需要自己补充另一条边的信息
    # 关闭文件
    f.close()

# 将原始图中的每一条边变为新顶点，然后删掉该边，并将新顶点与原边相连的顶点连接
def convertEdge():

    #新的转换方法：直接创建一个新的数组进行存储，然后将新数组反赋值给原始数组即可，以空间换时间，提高编码效率
    global maxVertexNum #该语句说明我下面用的是全局的变量，里面修改会影响外面的数据
    global maxEdgeNum   #该语句说明我下面用的是全局的变量，里面修改会影响外面的数据
    row = [0] * (maxVertexNum + maxEdgeNum)
    newArray = []
    for i in range(maxVertexNum + maxEdgeNum):
        newArray.append(row.copy())
    # newArray = [row] * (maxVertexNum + maxEdgeNum)
    k = maxVertexNum
    global edge
    for i in range(maxVertexNum):
        for j in range(maxVertexNum):
            if edge[i][j] == 1:
                newArray[i][k] = 1
                newArray[k][j] = 1
                newArray[k][i] = 1
                newArray[j][k] = 1
                k = k + 1
    edge = newArray.copy()
    maxVertexNum = maxVertexNum + maxEdgeNum #更新最大结点数为新的调整后的图的结点数
    pass


def initPointInfo():
    # 初始化顶点的所有后续需要用到的相关信息，仅初始化，不用于更新
    # 初始化顶点颜色列表，0代表没染色，1-?代表有颜色
    global point,nextNeighbor,nextNextNeighbor
    for i in range(maxVertexNum):
        p = pointC()
        point.append(p)

    #初始化邻居列表和邻居的邻居列表
    #初始化邻居列表

    for i in range(maxVertexNum):
        ts = set()  #存储邻居节点信息的临时集合
        nextNeighbor.append(ts)

        # 求i结点的邻居结点
        for j in range(maxVertexNum):
            if edge[i][j] == 1:
                nextNeighbor[i].add(j)
    del ts
    pass

    # 然后初始化邻居的邻居结点列表,求出来以后与邻居结点合并，得到两种邻居结点的并集

    for i in range(maxVertexNum):   #遍历每一个结点
        ts = set()  # 存储邻居节点信息的临时集合
        nextNextNeighbor.append(ts)
        for nb in nextNeighbor[i]:  #遍历当前结点的邻居列表，用nb迭代
            # 求nb结点的邻居结点（nb为遍历i结点的邻居结点列表的迭代变量）
            for j in range(maxVertexNum):
                if edge[nb][j] == 1:
                    nextNextNeighbor[i].add(j)
        nextNextNeighbor[i].remove(i) # 最后删除重复统计的自身结点
    del ts
    global nnnNeighbor
    nnnNeighbor.clear()
    for i in range(maxVertexNum):
        ts = nextNeighbor[i].union(nextNextNeighbor[i])
        nnnNeighbor.append(ts)
        del ts

    # 初始化totalSetList用于计算集合之差
    global totalSetList
    for i in range(maxVertexNum):
        totalSetList.add(i + 1)   #颜色列表从0开始计算
    pass

    #初始化一次颜色列表
    updateColor()

# 更新需要用到的信息
def updateColor():
    # 更新每个顶点相邻的顶点列表以及相邻顶点的相邻顶点的颜色列表
    global nnnColorList,point
    nnnColorList.clear()
    for i in range(maxVertexNum):
        ts = set()
        nnnColorList.append(ts)
        for j in nnnNeighbor[i]:
            nnnColorList[i].add(point[j].color)
    pass


def getFitness(seq):    # 功能为求一条染色体序列的适应度值，传入一个染色体序列，参数为数组seq，类型为list类型
    k = 1       # python中只需要对k作记录
    colorNumber = 1
    # 清除point的历史信息
    global point
    for i in range(maxVertexNum):
        point[i].color = 0
    for i in seq:   # i是顶点的序号，seq列表中的单项的值
        if point[i].color == 0:     # 顶点i目前还没有被染色
            # j = min(totalSetList - nnnNeighbor[i])
            j = min(totalSetList - nnnColorList[i])
            point[i].color = j
            if j > colorNumber:
                colorNumber = j
        updateColor()
        if k == maxVertexNum:
            break
        k = k + 1
    pass
    return colorNumber

def solve():
    # 规范注释规则：只在语句上面写注释，不在语句右面写注释
    # 读取图的数据文件
    files = ['','circle-3.txt','circle-4.txt','1-FullIns_3.wsc']
    readGraph(files[2])
    # 图转化
    convertEdge()
    #初始化顶点相关信息，只开始执行一次
    initPointInfo()
    # 测试序列：
    aarr = [[0,1,2,3,4,5], [0,3,1,4,2,5], [0,4,1,5,2,3],     #circle-3
            [0,1,2,3,4,5,6,7],[0,1,2,3,4,5,6,7],[0,1,2,3,4,5,6,7],  #circle-4
            [],[],[],
            [],[],[]]

    # 求适应度（测试）
    getFitness(aarr[4])
    #遗传选择变异过程：
    # if True:    #先只执行一次试试
    # while True: #暂未设置终止条件
    # 设置遗传的代数，变异的概率
    generations = 20
    crossProp = 0.8
    mutaProp = 0.2
    while generations >= 0:
        generations = generations - 1
        # 初始化种群
        popNum = 20      #种群个数
        pops = []
        for i in range(popNum):
            # 生成一个包含maxVertexNum个随机整数的列表
            tempList = [i for i in range(maxVertexNum)]
            pt = tempList.copy()
            random.shuffle(pt)
            pops.append(pt)
        pass
        #计算每一个子代的适应度
        global fites
        fites = [0] * popNum
        for i in range(popNum):
            fites[i] = getFitness(pops[i])
        #记录已经出现过的最小的着色数和着色序列
        global foundMinColorNum,foundMinColorNum
        if min(fites)<foundMinColorNum:
            foundMinColorNum = min(fites)
            foundMinPointSeq = pops[fites.index(foundMinColorNum)]
        pass

        #设置交叉概率,每个个体都是0.8的被选择概率，根据概率确定出最终产生多少个子代，算法为：子代个数 = 种群个体个数*0.8（因为要产生两个子代）
        #规定两个父代交叉之后不能再进行交叉操作，需要进行记录，使用set集合进行记录，只记录父编号，方便编码
        # numbers = list(range(0, popNum))  # 生成1到10的数字列表
        random_numbers = random.sample(range(0,popNum), int(popNum * 0.8))  # 从数字列表中随机选择5个数字
        # fms存储即将要进行交叉的双亲结点序号
        fms = set(random_numbers)
        newChilds = []  #存储交叉产生的子代
        for i in range(int(popNum * 0.8 / 2)): #要进行几次交叉
            #从集合中随机选择两个作为当前要交叉的父代
            #进行交叉过程完了以后的父代不能再参与交叉
            p1Num = random.choice(random_numbers)
            random_numbers.remove(p1Num)
            p2Num = random.choice(random_numbers)
            random_numbers.remove(p2Num)
            parent1 = pops[p1Num]
            parent2 = pops[p2Num]
            #LOX交叉
            #交叉出的子代加入到种群中，同时记录新子代的适应度值
            # 遗传
            # 轮盘赌选择，新型两点交叉LOX交叉
            # 随机生成两个数
            num1 = random.randint(0, maxVertexNum - 1)
            num2 = random.randint(0, maxVertexNum - 1)
            while num2 == num1:
                random.randint(0, maxVertexNum - 1)
            # 使用if语句比较大小并保存更小的那个数
            if num1 < num2:
                point1 = num1
                point2 = num2
            elif num1 > num2:
                point1 = num2
                point2 = num1
            # LOX交叉过程
            child1 = parent1.copy()
            child2 = parent2.copy()
            sf1 = parent1.copy()
            sf2 = parent2.copy()
            for i in range(point2-point1 + 1):
                child1[point1 + i] = parent2[point1 + i]
                sf2.remove(parent2[point1 + i])
                child2[point1 + i] = parent1[point1 + i]
                sf1.remove(parent1[point1 + i])
            # child1中其他结点为parent2中剩余结点（剩余的结点存储在sf2中），顺序为parent1中的这些节点的顺序
            # 方法：遍历parent1中的所有结点，如果遇到sf2中的结点则放入child1[i]中的位置
            for i in range(0,point1):
                for j in parent1:
                    if j in sf2:
                        child1[i] = j
                        sf2.remove(j)
                        break
                for j in parent2:

                    if j in sf1:
                        child2[i] = j
                        sf1.remove(j)
                        break

            for i in range(point2+1, maxVertexNum):
                for j in parent1:
                    if j in sf2:
                        child1[i] = j
                        sf2.remove(j)
                        break
                for j in parent2:
                    if j in sf1:
                        child2[i] = j
                        sf1.remove(j)
                        break


            pass
        #筛选出设置的种群大小数目个下一个种群，按照适应度从高到低筛选即可

        #变异，设置变异概率


if __name__ == '__main__':
    solve()
    pass

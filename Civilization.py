import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from pylab import *
plt.rcParams['font.sans-serif']=['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False  # 用来正常显示负号
class Civilization:
    '''
    文明的类，该类之中包括描述一个文明的全部信息
    '''
    def __init__(self,pos,star,Civi_Name):
        self.Civi_Name = Civi_Name # 文明的名字
        self.pos = pos  # 该文明的首府地点
        self.domain_stars = [star]  # 该文明的领地，包括很多Star实例
        self.civi_color = (np.random.rand()*0.8,np.random.rand()*0.8,np.random.rand()*0.8)  # 标记这个文明的颜色
        # 文明属性
        self.Living_Point = 1.0  # 生命值
        self.Tech_Point_Max = 0.0  # 到达过的最高技术值
        self.Tech_Point = 1.0  # 技术值
        self.Resource_Total = star.Resource_Point  # 1.0e15  # 文明属下占有的历史全部资源之和
        self.Resource_Point = star.Resource_Point  # 1.0e15  # 文明剩下的资源，是所有星系的资源之和
        self.Used_Resource_Point = 0  # 文明使用过的资源
        self.Used_Resource_Ratio = 0  # 文明资源使用率
        self.Living_Time = 0  # 存活时间
        self.Dead = False  # 文明是否死亡
        # 科技爆炸
        self.Tech_Explosion_Prob = 1/3000.0  # 技术爆炸的可能性
        self.Tech_Explosion_Num = 0  # 已经进行了几次科技革命
        self.Tech_Explosion_Bool = False  # 是否正在技术爆炸
        self.Tech_Explosion_Resttime = 0  # 科技革命剩下的时间
        self.Tech_Explosion_t = 0.02  # 技术爆炸的年化增长率
        # 天灾
        self.Disaster_Prob = 0.01  # 天灾的可能性
        self.Disaster_k_Tech = 0.97  # 天灾系数
        self.Disaster_k_Living = 0.95   # 天灾系数
        # 资源
        self.Resource_rt = 0.01  # 文明消耗资源的速度,来自技术
        self.Resource_rl = 0.01  # 文明消耗资源的速度,来自生命
        # 生命
        self.Living_l = 0.02  # 文明的生命值增加率
        self.Living_Resource_lr = 0.1  # 单位资源可以承载的人口上限
        self.Living_Tech_lt = 0.1 # 单位技术可以承载的人口上限
        # 军力值
        self.al = 1e-3
        self.at = 1e-3
        self.AC = self.al*self.Living_Point + self.at*self.Tech_Point
        # 历史
        self.history = ""
        self.dead_type = None
        # 宇宙相关参数
        self.p_expand = np.random.rand()*0.001
        # 文明政策
        self.alpha = np.random.rand()  # 生命值重要程度
        self.beta = np.random.rand()  # 技术值重要程度
        self.gama = np.random.rand()  # 资源值重要程度
        self.DarkForestStrike_p = 0.5  # 战争后，发动黑暗森林打击的可能
        self.War_p = 1-self.DarkForestStrike_p  # 战争后，发动战争的可能

    def refresh(self):
        if self.Dead:
            return
        self.Living_Time += 1
        # 更新资源值
        self.Resource_Point = 0.0
        for star in self.domain_stars:
            self.Resource_Point+=star.Resource_Point
        # 发生天灾
        if np.random.rand() < self.Disaster_Prob:
            self.Living_Point *= self.Disaster_k_Living
            self.Tech_Point *= self.Disaster_k_Tech
        # 没有技术爆炸才随机进行技术爆炸
        if not self.Tech_Explosion_Bool :
            if np.random.rand() < self.Tech_Explosion_Prob:
                self.Tech_Explosion_Bool = True
                self.Tech_Explosion_Resttime = np.random.randint(low=10,high=100)
                self.history+="公元{}年，开始第{}次科技革命，此次科技革命持续{}年\n".format(self.Living_Time,self.Tech_Explosion_Num + 1,self.Tech_Explosion_Resttime)
        self.Tech_Explosion_Resttime -= 1
        if self.Tech_Explosion_Bool:
            self.Tech_Point += self.Tech_Point * self.Tech_Explosion_t
        if self.Tech_Explosion_Resttime == 0:  # 技术革命结束
            self.Tech_Explosion_Bool = False
            self.Tech_Explosion_Num += 1
        if self.Tech_Point<=0.1:  # 退化文明死亡
            self.Tech_Point = 0.1
            self.set_Dead("Tech_Dead")
            return
        self.Tech_Point_Max = max(self.Tech_Point_Max,self.Tech_Point)
        # 每回合，资源都会减少
        this_year_Resource_Use = self.Tech_Point*self.Resource_rt + self.Living_Point*self.Resource_rl
        self.Resource_Point -= this_year_Resource_Use
        self.Used_Resource_Point += this_year_Resource_Use
        # 恒星系内的资源减少
        for st in self.domain_stars:
            st.Resource_Point -= this_year_Resource_Use / len(self.domain_stars)
        if self.Resource_Point<=0:  # 资源耗尽，文明死亡
            self.Resource_Point = 0
            self.set_Dead("Resource_Dead")
            return
        # 文明的生命值增加
        self.Living_Point += self.Living_Point*self.Living_l*(1-self.Living_Point/min(self.Resource_Point*self.Living_Resource_lr,self.Tech_Point*self.Living_Tech_lt))
        # 文明的生命值过低则死亡
        if self.Living_Point<1e-1:
            self.Living_Point=1e-1
            self.set_Dead("Living_Dead")
            return
        # 更新军力值
        self.AC = self.al * self.Living_Point + self.at * self.Tech_Point
        # 更新资源值
        self.Resource_Point = 0.0
        for st in self.domain_stars:
            self.Resource_Point += st.Resource_Point

    def get_Tech_Point(self):
        return self.Tech_Point
    def get_Used_Resource_Point(self):
        return self.Used_Resource_Point
    def get_Resource_Point(self):
        return self.Resource_Point
    def get_Living_Point(self):
        return self.Living_Point
    def is_Dead(self):
        return self.Dead
    def get_history(self):
        return self.history
    def set_Dead(self,dead_type):
        self.dead_type = dead_type
        self.Dead=True
        if dead_type=="Living_Dead":
            self.history += "公元{}年，人口消亡，文明灭绝\n".format(self.Living_Time)
        elif dead_type=="Resource_Dead":
            self.history += "公元{}年，资源耗尽，文明灭绝\n".format(self.Living_Time)
        elif dead_type=="Tech_Dead":
            self.history += "公元{}年，技术退化，文明灭绝\n".format(self.Living_Time)
        return
    def run_till_dead(self):
        while not self.is_Dead():
            self.refresh()
        return


if __name__ == '__main__':
    params=np.linspace(0.001,0.05,20)
    show_param = params
    yaozhes,gaojis,jishus,shoumins,ziyuans,baozhas=[],[],[],[],[],[]
    for p in params:
        living_years = []
        yaozhe = []
        gaoji = []
        techs = []
        ress = []
        te_nums = []
        for i in range(2000):
            c = Civilization((0,0,0),0)
            c.Tech_Explosion_t = p
            c.run_till_dead()
            living_years.append(c.Living_Time)
            yaozhe.append(c.Living_Time<500)
            techs.append(c.Tech_Point_Max)
            gaoji.append(c.Tech_Point_Max>1e6)
            ress.append(c.Used_Resource_Point)
            te_nums.append(c.Tech_Explosion_Num)
        yaozhe_ratio = np.mean(yaozhe)
        gaoji_ratio = np.mean(gaoji)
        tech_mean = np.mean(np.log10(techs))
        life_mean = np.mean(np.log10(living_years))
        ress_mean = np.mean(np.log10(ress))
        te_mean = np.mean(te_nums)
        print(p,yaozhe_ratio,gaoji_ratio,tech_mean,life_mean,ress_mean,te_mean)
        yaozhes.append(yaozhe_ratio)
        gaojis.append(gaoji_ratio)
        jishus.append(tech_mean)
        shoumins.append(life_mean)
        ziyuans.append(ress_mean)
        baozhas.append(te_mean)

    need_logx = False
    plt.subplot(2,3,1)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,yaozhes)
    plt.title("文明夭折比例")
    plt.subplot(2,3,2)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,gaojis)
    plt.title("高级文明比例")
    plt.subplot(2,3,3)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,baozhas)
    plt.title("平均技术爆炸次数")
    plt.subplot(2,3,4)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,jishus)
    plt.title("平均技术等级")
    plt.subplot(2,3,5)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,shoumins)
    plt.title("文明寿命等级")
    plt.subplot(2,3,6)
    if need_logx:
        plt.semilogx()
    plt.plot(show_param,ziyuans)
    plt.title("文明使用资源等级")
    plt.show()
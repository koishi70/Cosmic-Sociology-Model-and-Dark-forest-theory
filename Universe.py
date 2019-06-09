from Civilization import Civilization
from Star import Star
import numpy as np
import copy
import matplotlib.pyplot as plt
class Army:
    def __init__(self,from_civi,army_type,target,v):
        self.from_civi = from_civi  # 由哪个文明发出的
        self.army_type = army_type  # "Dark Forest Strike","army"
        self.ac = from_civi.AC  # 这个军队的军力值
        self.pos = from_civi.domain_stars[np.random.randint(low=0,high=len(from_civi.domain_stars))].pos  # 军队的位置
        self.target = target  # 军队的目标星系
        self.target_pos = target.pos  # 军队的目标星系的位置
        self.dist = self.d(self.target_pos,self.pos)# 距离目标的距离
        self.v = v  # 军队行进的速度大小
        self.v_dir = ((self.target_pos[0]-self.pos[0])/self.dist*self.v,(self.target_pos[1]-self.pos[1])/self.dist*self.v)
                        # 军队行进的v向量
        self.total_years = self.dist/self.v  # 预计行军年数
        self.arrived = False  # 是否到达目的地

    def d(self,a,b):
        return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def refresh(self):
        if not self.arrived:
            self.pos = (self.pos[0]+self.v_dir[0],self.pos[1]+self.v_dir[1])
        if self.d(self.pos,self.target_pos) < 0.2:
            self.arrived = True
        return


class Universe:
    '''
    宇宙的类，该类之中包括描述一个宇宙的全部信息
    '''
    def __init__(self, star_n,H,W):
        self.H = H
        self.W = W
        self.star_list = []  # 保存有宇宙内全部恒星的列表
        self.star_id = []  # 保存有宇宙内全部恒星ID的列表

        self.civi_list = []  # 保存有宇宙内全部文明的列表
        self.Civi_Gen = 0.001  # 每年，每个无主的恒星系诞生生命的概率
        self.civi_n = 0  # 迄今为止有多少文明出现

        self.army_list = []  # 保存有所有的军队情况，黑暗森林打击等等

        self.TC_interstellar = 1e3  # 星际时代的技术值门槛
        self.TC_super = 1e10  # 技术值超过这个，达到光速
        self.q = 0.1  # 反败为胜概率
        self.p = 0.5  # 准备好战争后生命损失减少
        self.brocast_d = 400 # 多少距离内的可以听到宇宙广播

        self.history = ""  # 宇宙历史事件

        # 初始随机分布有恒星系
        def random_init_resource_point():
            return np.power(10,np.random.uniform(low=5,high=15))
        def random_init_pos(H,W):
            return (np.random.rand()*H,np.random.rand()*W)
        for i in range(star_n):
            pos = random_init_pos(H,W)
            Init_Resource_Point = random_init_resource_point()
            st = Star(pos=pos,Init_Resource_Point=Init_Resource_Point)
            self.star_list.append(st)
            self.star_id.append(f"Star_{i}")

    def get_max_v(self,TC):
        #根据文明的技术值得到这个文明的星际宇航速度
        if TC<self.TC_interstellar:
            return 0
        elif TC>self.TC_super:
            return 1
        else:
            log10v = np.log10(self.TC_interstellar)/np.log10(self.TC_super/self.TC_interstellar)*(np.log10(TC)-np.log10(self.TC_super))
            return np.power(10,log10v)

    def d(self, a, b):
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_nearest_star(self,from_civi):
        # 得到距离这个文明最近的，非本文明星系,从最近的5个里面随机选择
        ans = []
        for star in self.star_list:
            if star not in from_civi.domain_stars:  # 如果不是这个文明的领土，纳入计算
                ans.append((star,self.d(star.pos,from_civi.pos)))
        ans = sorted(ans,key=lambda x:x[1])
        if len(ans)==0:
            return None
        i = np.random.randint(low=0, high=min(10,len(ans)))
        return ans[i][0]

    def with_prob(self,p):  # 以一定概率p返回true
        if np.random.rand()<p:return True
        else:return False

    def gen_civi(self,star):  # 生成一个文明
        c = Civilization(star.pos,star,f"Civi_{self.civi_n}")
        self.civi_list.append(c)
        self.civi_n += 1
        return c

    def refreash(self):
        # 过去一个宇宙年
        # 随机生成文明
        for st in self.star_list:
            if not st.Have_Life:
                if self.with_prob(self.Civi_Gen):
                    st.Have_Life = True
                    civi = self.gen_civi(st)
                    st.domained_by_civi = civi
                    #print(f"在恒星{self.star_id[self.star_list.index(st)]}上诞生了一个文明{self.civi_id[-1]}")
        return

    def total_refreash(self):  # 整合的全部刷新
        # 宇宙刷新
        self.refreash()
        # 宇宙所有文明发展
        for civi in self.civi_list:
            civi.refresh()
        # 刷新所有的军队位置
        for army in self.army_list:
            army.refresh()
        # 发动战争
        for civi in self.civi_list:
            if civi.Tech_Point >self.TC_interstellar: # 可以进行星际移民
                if self.with_prob(civi.p_expand):  # 有一定概率进行星际移民，派出军队
                    v=self.get_max_v(civi.Tech_Point)
                    # 目标星系是最近的那个星系
                    target_star = self.get_nearest_star(from_civi=civi)
                    if target_star is None:# 没有剩余的星系了
                        continue
                    army = Army(army_type="army",from_civi=civi,target=target_star,v=v)
                    self.army_list.append(army)
        # 当军队抵达目的地，开始进行博弈
        for army in self.army_list:
            if army.arrived:
                if army.target.domained_by_civi is None and army.army_type=="army": # 目的地无主，直接占有
                    army.target.Have_Life = True
                    army.target.domained_by_civi = army.from_civi
                    army.from_civi.domain_stars.append(army.target)
                    army.arrived = True
                elif army.target.domained_by_civi is not None and army.army_type=="Dark Forest Strike": # 黑暗森林打击
                    army.target.Have_Life = False
                    army.target.domained_by_civi.domain_stars.remove(army.target)
                    if len(army.target.domained_by_civi.domain_stars)==1:
                        army.target.domained_by_civi.Dead=True
                    army.target.domained_by_civi = None
                elif army.target.domained_by_civi is army.from_civi:  # 目的地就是自家领地
                    continue
                else:  # 目的地有主，开始进行透明博弈
                    # 有一定可能直接发动战争
                    if self.with_prob(army.from_civi.War_p):
                        if army is None or army.target is None:
                            continue
                        # 计算概率
                        my_AC,enemy_AC = army.from_civi.AC,army.target.domained_by_civi.AC
                        win_AC,lose_AC = max(my_AC,enemy_AC),min(my_AC,enemy_AC)
                        my_RC,enemy_RC = army.from_civi.Resource_Point,army.target.domained_by_civi.Resource_Point
                        win_RC, lose_RC = my_RC,enemy_RC
                        if my_AC<enemy_AC:
                            win_RC, lose_RC = lose_RC,win_RC
                        win_civi,lose_civi = army.from_civi,army.target.domained_by_civi
                        if my_AC<enemy_AC:
                            win_civi, lose_civi = lose_civi,win_civi
                        win_war = 1-(1-self.p)/(1+(lose_civi.gama*lose_RC)/(lose_civi.alpha*win_AC))
                        win_quiet = 1-win_war
                        lose_war =  1-(1-self.p)/(1+(win_civi.gama*lose_RC)/(win_civi.alpha*win_AC))
                        lose_quiet = 1- lose_war
                        # 随机选择
                        win_choose_war = self.with_prob(win_war)
                        lose_choose_war = self.with_prob(lose_war)
                        # 双方都寂静，什么都不发生
                        if not win_choose_war and not lose_choose_war:
                            continue
                        # 发生战争，强者灭绝弱者，并将弱者的领地资源据为己有
                        lose_civi.Dead=True
                        for star in lose_civi.domain_stars:
                            star.domained_by_civi = win_civi
                        win_civi.domain_stars.extend(lose_civi.domain_stars)
                        # 强者也会受伤
                        win_civi.Living_Point -= lose_civi.AC
                    else: # 选择黑暗森林打击
                        heard_civi = []  # 听到宇宙广播的文明
                        for civi in self.civi_list:
                            if civi is not army.from_civi and self.d(army.from_civi.pos,civi.pos)<self.brocast_d:
                                heard_civi.append(civi)
                        for civi in heard_civi:
                            if self.with_prob(1-1/(1+self.q)) and civi.Tech_Point>self.TC_super:
                                dark_forest_strike = Army(army_type="Dark Forest Strike",from_civi=civi,target=army.target,
                                                          v=self.get_max_v(civi.Tech_Point))
                                self.army_list.append(dark_forest_strike)
                                try:
                                    print(civi.Civi_Name,"黑暗森林打击",army.target.domained_by_civi.Civi_Name)
                                except:pass

        # 军队抵达后清除
        new_army_list = []
        for army in self.army_list:
            if army.v==0:
                continue
            if army.from_civi not in self.civi_list:
                continue
            if not army.arrived and army.from_civi is not army.target.domained_by_civi and self.d(army.pos,army.target.pos)>0.2:
                new_army_list.append(army)
        self.army_list = new_army_list
        # 恒星资源耗尽，就清除出去
        new_star_list = []
        for star in self.star_list:
            if star.Resource_Point > 0:
                new_star_list.append(star)
        self.star_list = new_star_list
        # 有时出现的一个星系多个文明,强行删除弱小的文明
        for civi in self.civi_list:
            civi.domain_stars = list(set(civi.domain_stars))
            for star in civi.domain_stars:
                if star.domained_by_civi is None:
                    star.domained_by_civi=civi
                if star.domained_by_civi is not civi:
                    if civi.Tech_Point<star.domained_by_civi.Tech_Point:
                        civi.Dead = True
                        break
                    else:
                        star.domained_by_civi.Dead = True
                        break
        # 文明灭绝则清除出去
        new_civi_list = []
        for civi in self.civi_list:
            if not civi.Dead:
                new_civi_list.append(civi)
            else:  # 文明灭绝
                for st in civi.domain_stars:
                    st.Have_Life = False
                    st.domained_by_civi = None
        self.civi_list = new_civi_list
        return

    def show_all_star(self):
        #  显示宇宙边界
        '''
        boundary_color = (0.2, 0.2, 0.2)
        plt.hlines(y=0, xmin=0, xmax=self.W, linestyles="--", color=boundary_color)
        plt.hlines(y=self.H, xmin=0, xmax=self.W, linestyles="--", color=boundary_color)
        plt.vlines(x=0, ymin=0, ymax=self.H, linestyles="--", color=boundary_color)
        plt.vlines(x=self.W, ymin=0, ymax=self.H, linestyles="--", color=boundary_color)
        '''
        # 显示所有恒星
        plt.xlim([0, self.W])
        plt.ylim([0, self.H])
        star_xs, star_ys, star_ss, star_cs = [], [], [], []
        for star in self.star_list:
            star_xs.append(star.pos[0])
            star_ys.append(star.pos[1])
            star_cs.append((0,0,0))#((np.log10(star.Resource_Point) / 15, 0, 0))
            star_ss.append(np.log10(star.Resource_Point))
        for st in self.star_list:
            plt.scatter(star_xs, star_ys, s=star_ss, c=star_cs)
        return

    def show_all_civi(self):
        plt.xlim([0, self.W])
        plt.ylim([0, self.H])
        # 显示所有的文明
        civi_xs, civi_ys, civi_ss, civi_cs,civi_ts = [], [], [], [], []
        for civi in self.civi_list:
            for domain_star in civi.domain_stars:
                if domain_star.domained_by_civi is civi:
                    civi_xs.append(domain_star.pos[0])
                    civi_ys.append(domain_star.pos[1])
                    civi_ss.append(40*np.log10(civi.Living_Point) + 10)
                    civi_cs.append(civi.civi_color)
        plt.scatter(civi_xs, civi_ys, s=civi_ss, c=civi_cs)
        for civi in self.civi_list:
            for domain_star in civi.domain_stars:
                plt.text(domain_star.pos[0], domain_star.pos[1]+0.01*(40*np.log10(civi.Living_Point) + 10),
                         civi.Civi_Name,fontdict={'size': 10, 'color': 'b'})
        return

    def show_all_army(self):
        # 显示所有的军队情况
        army_xs, army_ys, army_ss, army_cs,army_ts,army_ms = [], [], [], [],[],[]
        for army in self.army_list:
            if army.army_type=="army":
                army_xs.append(army.pos[0])
                army_ys.append(army.pos[1])
                army_ss.append(10)
                army_cs.append(army.from_civi.civi_color)
        plt.scatter(army_xs, army_ys, s=army_ss, c=army_cs,marker="^")
        army_xs, army_ys, army_ss, army_cs, army_ts, army_ms = [], [], [], [], [], []
        for army in self.army_list:
            if army.army_type == "Dark Forest Strike":
                army_xs.append(army.pos[0])
                army_ys.append(army.pos[1])
                army_ss.append(15)
                army_cs.append(army.from_civi.civi_color)
        plt.scatter(army_xs, army_ys, s=army_ss, c=army_cs, marker="x")
        #for army in self.army_list:
        #    plt.text(army.pos[0], army.pos[1], f"Army_{army.from_civi.Civi_Name[5:]}",fontdict={'size': 10, 'color': 'b'})
        return

    def show_order(self):
        # 显示本宇宙文明的排名情况
        civis = []
        for civi in self.civi_list:
            civis.append({"id":civi.Civi_Name,"color":civi.civi_color,
                          "LC":np.log10(civi.Living_Point),"TC":np.log10(civi.Tech_Point),"RC":np.log10(civi.Resource_Point)})
        orders = ["TC","LC","RC"]
        for order_by in orders:
            civis = sorted(civis,key=lambda x:x[order_by],reverse=True)
            best = 5
            for i in range(min(best,len(self.civi_list))):
                text =f"{order_by} No.{i+1} id:{civis[i]['id']} {round(civis[i][order_by],3)}\n"
                plt.text(-self.W*0.14,self.H*0.03*(best-1-i) + self.H*orders.index(order_by)*0.2,text,
                         fontdict={'size': 11, 'color': civis[i]['color']})

    def Show_Universe(self,save=False):
        show_per_year = 1000
        all_year = 1000000
        plt.figure(figsize=(18,9))
        plt.xlim([0, self.W])
        plt.ylim([0, self.H])
        if not save:
            plt.ion()
        for it in range(int(all_year/show_per_year)):
            if not save:
                plt.pause(0.001)
            plt.clf()
            plt.title(f"Universe year:{it*show_per_year} exist civi:{len(self.civi_list)} exist army:{len(self.army_list)}")
            # 刷新一段时间
            for i in range(show_per_year):
                try:
                    self.total_refreash()
                except:continue
            self.show_all_star()
            self.show_all_civi()
            self.show_all_army()
            self.show_order()
            if save:
                plt.savefig(f"out/{it}.png")
        if not save:
            plt.ioff()
            plt.show()

if __name__ == '__main__':
    universe = Universe(star_n=100,H=200,W=200)
    universe.Show_Universe(save=True)

class Star:
    '''
    恒星系的类，该类之中包括描述一个恒星系的全部信息
    '''

    def __init__(self,pos,Init_Resource_Point):
        self.pos = pos  # 恒星系的位置，不变
        self.Resource_Point = Init_Resource_Point  # 恒星系的初始资源值
        self.Have_Life = False   # 恒星系内有文明
        self.domained_by_civi = None  # 恒星系被哪个文明控制





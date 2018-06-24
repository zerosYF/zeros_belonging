import wx
from my_detect import video_detect
from my_detect import monitor_detect
import pymysql
class MainFrame(wx.Frame):
    info=[]
    video_table_name=""
    monitor_table_name=""
    #数据库配置信息
    def __init__(self):
        wx.MDIParentFrame.__init__(self,None,-1,"检测器",size=(800,600))
        self.box=wx.BoxSizer(wx.VERTICAL)
        self.UI_init()
        self.Show(True)

    def UI_init(self):
        bar=wx.MenuBar()

        modal_select=wx.Menu()
        self.vd_detect=wx.MenuItem(modal_select,8086,text="视频检测",kind=wx.ITEM_NORMAL)
        self.mn_detect=wx.MenuItem(modal_select,8087,text="监控检测",kind=wx.ITEM_NORMAL)
        modal_select.Append(self.vd_detect)
        modal_select.Append(self.mn_detect)
        bar.Append(modal_select,"&模式选择")

        db_ini=wx.Menu()
        db_configure=wx.MenuItem(db_ini,8088,text="基本配置",kind=wx.ITEM_NORMAL)
        db_ini.Append(db_configure)
        db_info=wx.MenuItem(db_ini,8089,text="当前信息",kind=wx.ITEM_NORMAL)
        db_ini.Append(db_info)
        video_table=wx.MenuItem(db_ini,8090,text="视频检测数据表",kind=wx.ITEM_NORMAL)
        db_ini.Append(video_table)
        monitor_table=wx.MenuItem(db_ini,8091,text="监控检测数据表",kind=wx.ITEM_NORMAL)
        db_ini.Append(monitor_table)

        bar.Append(db_ini,"&数据库配置")


        help_info=wx.Menu()
        help_panel=wx.MenuItem(help_info,8092,text="帮助信息",kind=wx.ITEM_NORMAL)
        help_info.Append(help_panel)
        bar.Append(help_info,"&其他信息")
        self.SetMenuBar(menuBar=bar)

        self.vd = video_detect.MyFrame(self)
        self.box.Add(self.vd, 1, wx.EXPAND)
        self.mn = monitor_detect.MyFrame(self)
        self.box.Add(self.mn,1,wx.EXPAND)
        self.box.Show(self.vd)
        self.box.Hide(self.mn)
        self.SetSizer(self.box)

        self.Bind(wx.EVT_MENU, self.to_video, id=8086)
        self.Bind(wx.EVT_MENU, self.to_monitor, id=8087)
        self.Bind(wx.EVT_MENU,self.to_dbconf,id=8088)
        self.Bind(wx.EVT_MENU,self.get_db_info,id=8089)
        self.Bind(wx.EVT_MENU,self.to_videoconf,id=8090)
        self.Bind(wx.EVT_MENU,self.to_monitorconf,id=8091)
        self.Bind(wx.EVT_MENU,self.gethelp,id=8092)

    def gethelp(self,evt):
        wx.MessageBox("数据库最好使用mysql；"
                      "\n在视频检测中，导入视频为中文名;"
                      "\n在监控中，一般事先连接好数据库;"
                      "\n事件仓促，准确率较低;"
                      "\n红色框为未戴安全帽;"
                      "\n绿色框为已戴或者无法检测人头位置;","帮助信息")

    def get_db_info(self,evt):
        if len(self.info)!=0:
            wx.MessageBox("主机:"+self.info[0]
                          +"\n端口号:"+self.info[1]
                          +"\n数据库:"+self.info[2],"当前配置")
        else:
            wx.MessageBox("未配置当前数据库","提示")

    def to_video(self,evt):
        self.box.Hide(self.mn)
        self.box.Show(self.vd)
        self.box.Layout()
        #必须添加layout方法强制重绘；

    def to_monitor(self,evt):
        self.box.Hide(self.vd)
        self.box.Show(self.mn)
        self.box.Layout()

    def to_dbconf(self,evt):
        self.db_dlg=MyDialog(parent=self,title="数据库配置")
        if self.db_dlg.ShowModal()==wx.ID_OK:
            self.info=self.db_dlg.rtn_db_info()
            result=pymysql.connect(host=self.info[0],user=self.info[3],
                                   port=int(self.info[1]),db=self.info[2],
                                   password=self.info[4],charset='utf8')
            if result:
                wx.MessageBox("尝试连接成功","提示")
                self.vd.set_db_info(self.info)
                self.mn.set_db_info(self.info)
            else:
                wx.MessageBox("尝试连接失败,请检查配置","提示")
                self.info.clear()

    def to_videoconf(self,evt):
        if len(self.info)==0:
            wx.MessageBox("请先进行数据库配置","提示")
            return
        video_dlg=table_init_dlg(parent=self,title="视频表设置")
        if video_dlg.ShowModal()==wx.ID_OK:
            sqlconnect = pymysql.connect(host=self.info[0], user=self.info[3],
                                     port=int(self.info[1]), db=self.info[2],
                                     password=self.info[4], charset='utf8')
            if sqlconnect==False:
                wx.MessageBox("数据库有问题,设置失败","提示")
                return
            table_name=video_dlg.rtn_table_name()
            try:
                cur=sqlconnect.cursor()
                sql2="create table if not exists %s (" \
                    "id int(10) not null primary key auto_increment," \
                    "filename char(20) not null," \
                    "capped int(10) null," \
                    "nocapped int(10) null," \
                    "frame_num int(10) null" \
                    ")"%table_name
                cur.execute(sql2)
                sqlconnect.commit()
                self.vd.table_name = table_name
            except pymysql.Error:
                sqlconnect.rollback()
            finally:
                cur.close()
                sqlconnect.close()
                if self.vd.table_name=="":
                    wx.MessageBox("设置出了问题，请检查数据库", "提示")



    def to_monitorconf(self,evt):
        if len(self.info)==0:
            wx.MessageBox("请先进行数据库配置","提示")
            return
        monitor_dlg=table_init_dlg(parent=self,title="监控表设置")
        if monitor_dlg.ShowModal()==wx.ID_OK:
            sqlconnect = pymysql.connect(host=self.info[0], user=self.info[3],
                                     port=int(self.info[1]), db=self.info[2],
                                     password=self.info[4], charset='utf8')
            if sqlconnect == False:
                wx.MessageBox("数据库有问题,设置失败", "提示")
                return
            table_name = monitor_dlg.rtn_table_name()
            try:
                cur = sqlconnect.cursor()
                sql2 = "create table if not exists %s (" \
                        "id int(10) not null primary key auto_increment," \
                        "this_time datetime default CURRENT_TIMESTAMP," \
                        "nocapped_num int(10)" \
                        ")" % table_name
                cur.execute(sql2)
                sqlconnect.commit()
            except pymysql.Error:
                sqlconnect.rollback()
            finally:
                cur.close()
                try:
                    with sqlconnect.cursor() as cur2:
                        sql3 = "insert into %s (nocapped_num) values (0)" % table_name
                        cur2.execute(sql3)
                        sqlconnect.commit()
                        self.mn.table_name = table_name
                except pymysql.Error:
                    sqlconnect.rollback()
                finally:
                    if self.mn.table_name == "":
                        wx.MessageBox("设置出了问题，请检查数据库", "提示")

class MyDialog(wx.Dialog):
    def __init__(self,parent,title):
        super(MyDialog,self).__init__(parent=parent,title=title,size=(250,300))
        self.box=wx.BoxSizer(wx.VERTICAL)
        self.box1=wx.BoxSizer(wx.HORIZONTAL)
        self.box2=wx.BoxSizer(wx.HORIZONTAL)
        self.box3=wx.BoxSizer(wx.HORIZONTAL)
        self.box4 = wx.BoxSizer(wx.HORIZONTAL)
        self.box5 = wx.BoxSizer(wx.HORIZONTAL)
        self.box6 = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl1=wx.StaticText(self,label="主机名",style=wx.ALIGN_CENTER)
        self.lbl2=wx.StaticText(self,label="端口号",style=wx.ALIGN_CENTER)
        self.lbl3 = wx.StaticText(self, label="数据库名",style=wx.ALIGN_CENTER)
        self.lbl4 = wx.StaticText(self, label="用户名",style=wx.ALIGN_CENTER)
        self.lbl5 = wx.StaticText(self, label="密码",style=wx.ALIGN_CENTER)
        self.host_box=wx.TextCtrl(self)
        self.port_box=wx.TextCtrl(self)
        self.db_box=wx.TextCtrl(self)
        self.user_box=wx.TextCtrl(self)
        self.psd_box=wx.TextCtrl(self,style=wx.TE_PASSWORD)
        self.ok_btn=wx.Button(self,wx.ID_OK)
        self.ccl_btn=wx.Button(self,wx.ID_CANCEL)
        self.box1.Add(self.lbl1,wx.ALL|wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box1.Add(self.host_box,wx.ALL|wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box2.Add(self.lbl2,wx.ALL|wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box2.Add(self.port_box,wx.ALL|wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box3.Add(self.lbl3, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box3.Add(self.db_box, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box4.Add(self.lbl4, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box4.Add(self.user_box, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box5.Add(self.lbl5, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box5.Add(self.psd_box, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box6.Add(self.ok_btn, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box6.Add(self.ccl_btn, wx.ALL | wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL,10)
        self.box.Add(self.box1, wx.ALL|wx.SHAPED,10)
        self.box.Add(self.box2, wx.ALL|wx.SHAPED,10)
        self.box.Add(self.box3, wx.ALL|wx.SHAPED,10)
        self.box.Add(self.box4, wx.ALL|wx.SHAPED,10)
        self.box.Add(self.box5, wx.ALL|wx.SHAPED,10)
        self.box.Add(self.box6, wx.ALL|wx.SHAPED,10)
        self.SetSizer(self.box)

    def rtn_db_info(self):
        info=[]
        info.append(self.host_box.GetValue())
        info.append(self.port_box.GetValue())
        info.append(self.db_box.GetValue())
        info.append(self.user_box.GetValue())
        info.append(self.psd_box.GetValue())
        return info

class table_init_dlg(wx.Dialog):
    def __init__(self,parent,title):
        super(table_init_dlg,self).__init__(parent=parent,title=title,size=(300,150))
        self.box=wx.BoxSizer(wx.VERTICAL)
        self.panel1=wx.Panel(self)
        self.panel2=wx.Panel(self)
        self.table_name_box=wx.TextCtrl(self.panel1)
        self.table_ok=wx.Button(self.panel2,id=wx.ID_OK,size=(55,30),pos=(220,10))
        self.box.Add(self.panel1,1,wx.ALL|wx.EXPAND)
        self.box.Add(self.panel2,1,wx.ALL|wx.EXPAND)
        self.SetSizer(self.box)

    def rtn_table_name(self):
        return self.table_name_box.GetValue()

base=wx.App(False)
frame=MainFrame()
base.MainLoop()
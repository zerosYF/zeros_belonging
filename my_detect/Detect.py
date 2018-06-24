import pymysql
import os
import cv2
import winsound
from time import sleep

import pymysql.cursors
import wx
import wx.media
import numpy as np
import threading
from imutils.object_detection import non_max_suppression
import ctypes

try:
    temp=ctypes.windll.LoadLibrary('opencv_ffmpeg341.dll')
except:
    print("load binary failed")
    pass

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

        self.vd = MyFrame2(self)
        self.box.Add(self.vd, 1, wx.EXPAND)
        self.mn = MyFrame1(self)
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


class MyFrame1(wx.Panel):
    isalert=False
    doalert=False
    db_info=[]
    table_name=""
    n=0
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        self.box=wx.BoxSizer(wx.HORIZONTAL)
        self.control_box=wx.BoxSizer(wx.VERTICAL)
        self.UI_init()
        self.SetSizer(self.box)
        self.isdisplay=False
        self.isdetect=False

    def set_db_info(self,db_info):
        self.db_info=db_info

    def UI_init(self):
        self.monitor_panel=wx.Panel(self)
        self.monitor_panel.SetBackgroundColour(wx.BLACK)
        self.monitor_display = wx.StaticBitmap(self.monitor_panel)
        self.box.Add(self.monitor_panel,3,wx.ALL|wx.EXPAND,10)
        self.button1=wx.Button(self,id=1111,label="开启监控")
        self.control_box.Add(self.button1,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)
        self.button1.Bind(wx.EVT_BUTTON,self.display)
        self.button3=wx.Button(self,id=1113,label="导出数据")
        self.control_box.Add(self.button3,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)
        self.button3.Bind(wx.EVT_BUTTON,self.LeadOut)
        self.button4=wx.Button(self,id=1114,label="开启报警模式")
        self.control_box.Add(self.button4,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)
        self.button4.Bind(wx.EVT_BUTTON,self.start_alert)
        self.box.Add(self.control_box,1,wx.EXPAND)

    def display(self,evt):
        if self.isdisplay==False:
            self.isdisplay=True
            self.button1.SetLabel("暂停监控")
            self.cap = cv2.VideoCapture(0)
            import threading
            threading._start_new_thread(self.display_thread,())
            threading._start_new_thread(self.store_thread,())
        else:
            self.button1.SetLabel("开启监控")
            self.isdisplay = False


    def store_thread(self):
        if len(self.db_info)==0:
            wx.MessageBox("无法写入,请确认数据库信息","提示")
            return
        self.sqlconnect = pymysql.connect(host=self.db_info[0], user=self.db_info[3],
                                          port=int(self.db_info[1]),
                                          db=self.db_info[2], charset='utf8')
        if self.sqlconnect==False:
            wx.MessageBox("连接数据库出错","提示")
            return

        if self.table_name=="":
            wx.MessageBox("清闲设置存储监控存储数据表","提示")
            return

        self.cur = self.sqlconnect.cursor()
        while self.isdisplay:
            self.StoreData()
            self.n = 0
            sleep(5)#5秒写入一次
        self.cur.close()
        self.sqlconnect.close()


    def display_thread(self):

        while (self.isdisplay):
            ret, frame = self.cap.read()
            height, width = frame.shape[:2]
            detected_frame=self.labeling(frame)
            images = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width=width, height=height, data=images)
            pic.SetSize(self.monitor_panel.GetSize())
            self.monitor_display.SetBitmap(pic)
        self.cap.release()

    def LeadOut(self,evt):
        if len(self.db_info)==0:
            wx.MessageBox("未配置数据库，请先设置","提示")
            return
        sqlconnect = pymysql.connect(host=self.db_info[0],user=self.db_info[3],
                                          passwd=self.db_info[4],port=int(self.db_info[1]),
                                          db=self.db_info[2],charset='utf8')
        if sqlconnect==False:
            wx.MessageBox("连接数据库出错，请检查","提示")
            return

        if self.table_name=="":
            wx.MessageBox("请先设置监控存储数据表","提示")
            return

        cur=self.sqlconnect.cursor()
        sql="select * from %s"%self.table_name
        cur.execute(sql)
        result=cur.fetchall()
        if cur.rowcount==0:
            wx.MessageBox("没有记录，无法导出","提示")
            cur.close()
            sqlconnect.close()
            return
        try:
            import csv
            wildcard="*.csv"
            dlg=wx.FileDialog(self,"新建导出数据",os.getcwd(),"",wildcard,wx.FD_SAVE)
            if dlg.ShowModal()==wx.ID_OK:
                with open(dlg.GetPath(),'w') as csvfile:
                    wr=csv.writer(csvfile)
                    wr.writerow(['id','截止日期','未佩戴安全帽数量'])
                    for eash in result:
                        wr.writerow([items for items in eash])
            wx.MessageBox("导出成功!","提示")
        finally:
            cur.close()
            sqlconnect.close()


    def start_alert(self,evt):
        if self.isalert:
            self.isalert=False
            self.button4.SetLabel("开启报警模式")
        else:
            self.isalert=True
            threading._start_new_thread(self.alert_thread,())
            self.button4.SetLabel("关闭报警模式")

    def alert_thread(self):
        while self.isalert:#开关控制；
            if self.doalert:
                #检测控制；
                winsound.PlaySound("901028.wav",winsound.SND_FILENAME)
                self.doalert=False

    def labeling(self,frame):
        hog = cv2.HOGDescriptor()
        hog.load("myHogDector1.bin")
        # hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        (rects, weights) = hog.detectMultiScale(frame,
                                                winStride=(4, 4), padding=(8, 8), scale=1.05)
        rects_with_wh=np.array([(x,y,x+w,y+h) for (x,y,w,h) in rects])
        pick=non_max_suppression(rects_with_wh,probs=None,overlapThresh=0.3)
        for (xA, yA, xB, yB) in pick:
            pick_img=frame[yA:yB,xA:xB]
            result=self.capped(pick_img)
            if result==0:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
            elif result==1:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 0, 255), 2)
                self.doalert=True
                self.n+=1
        return frame

    def capped(self,pick):
        result= test(pick)
        if result==0:
            return 0
        elif result==1:
            return 1
        else:
            return 2

    def StoreData(self):
        try:
            sql1 = "select * from %s where id=(select max(id) from %s)"\
                   %(self.table_name,self.table_name)
            self.cur.execute(sql1)
            last_nocapped_num = self.cur.fetchone()[-1]
            now_num = last_nocapped_num + self.n
            sql2 = "insert into %s (nocapped_num) values (%d)" % (self.table_name,now_num);
            self.cur.execute(sql2)
        except pymysql.Error as e:
            wx.MessageBox("导入失败,请检查数据库","提示");
            print(e)

    def IsBeingDeleted(self):
        self.isdisplay=False
        self.isalert=False
        super(self).IsBeingDeleted(self)

    def Destroy(self):
        self.isdisplay = False
        self.isalert = False
        super(self).Destroy(self)





class MyFrame2(wx.Panel):

    import_video_path=""
    import_video_father_path=""
    capped_num=0
    nocapped_num=0
    frame_num=0
    cancel_get_video=False
    load_ok=False

    db_info=[]
    table_name=""
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)
        self.SetBackgroundColour(wx.WHITE)
        self.box=wx.BoxSizer(wx.HORIZONTAL)
        self.controlbox=wx.BoxSizer(wx.VERTICAL)
        self.UI_init()
        self.SetSizer(self.box)

    def set_db_info(self,db_info):
        self.db_info=db_info

    def UI_init(self):
        self.button1 = wx.Button(self, label="导入视频")
        self.button1.Bind(wx.EVT_BUTTON, self.OnButtonClick1)
        self.controlbox.Add(self.button1,1,
                            wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)
        self.button2 = wx.Button(self, label="导出数据")
        self.button2.Bind(wx.EVT_BUTTON,self.LeadOut)
        self.controlbox.Add(self.button2,1,
                            wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)
        self.button3 = wx.Button(self, label="写入当前数据")
        self.button3.Bind(wx.EVT_BUTTON, self.StoreData)
        self.controlbox.Add(self.button3,1,
                            wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.SHAPED,10)

        self.mc = wx.media.MediaCtrl(self, pos=(20, 20))
        self.mc.ShowPlayerControls()
        self.box.Add(self.mc,3,wx.ALL|wx.EXPAND,10)
        self.box.Add(self.controlbox,1,wx.EXPAND)

    def OnButtonClick1(self,evt):
        wildcard="*.avi|*.mp4"
        dlg=wx.FileDialog(self,"选择视频文件",os.getcwd(),"",wildcard,wx.FD_OPEN)
        if dlg.ShowModal()==wx.ID_OK:

            self.load_ok = False
            self.cancel_get_video=False

            if self.import_video_father_path!="":
                os.remove(self.import_video_father_path+"\labeled_video.avi")
            self.import_video_path=dlg.GetPath()
            self.import_video_father_path='\\'.join(self.import_video_path.split('\\')[0:-1])

            print("track there")
            threading._start_new_thread(self.detect,())
            self.mc.Load(self.import_video_father_path + "\labeled_video.avi")
            self.opr_dlg = Mydialog(parent=self, title="提示")
            if self.opr_dlg.ShowModal() == wx.ID_CANCEL:
                self.CancelGet()

    def CancelGet(self):
        self.cancel_get_video=True
        self.writer.release()
        self.cap.release()
        if self.import_video_father_path!="" or self.load_ok==False:
            os.remove(self.import_video_father_path+"\labeled_video.avi")
            self.import_video_father_path=""

    def detect(self):
        self.cap = cv2.VideoCapture(self.import_video_path)
        self.out_fps = 24
        self.size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.writer = cv2.VideoWriter(
            self.import_video_father_path+"\labeled_video.avi",
            cv2.VideoWriter_fourcc('M', 'P', '4', '2'),
            self.out_fps,self.size)

        print(self.import_video_path)
        nFrames=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(nFrames)
        for i in range(nFrames):
            ret,frame=self.cap.read()
            if i%5==0:
                labeled_frame=self.labeling(frame)
                self.writer.write(labeled_frame)
            if self.cancel_get_video==True:
                self.load_ok==False
                break
        print("detect function willing cancel")
        if self.cancel_get_video==False:
            self.writer.release()
            self.cap.release()
            self.load_ok=True
            sleep(1)
            self.opr_dlg.EndModal(wx.ID_OK)
            wx.MessageBox("处理成功","成功");


    def labeling(self,frame):
        hog = cv2.HOGDescriptor()
        hog.load("myHogDector1.bin")
        #hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        (rects, weights) = hog.detectMultiScale(frame,
                                                winStride=(4, 4), padding=(8, 8), scale=1.05)
        rects_without_wh=np.array([(x,y,x+w,y+h) for (x,y,w,h) in rects])
        pick=non_max_suppression(rects_without_wh,probs=None,overlapThresh=0.3)
        #非极大限制去掉多余选框;
        for (xA, yA, xB, yB) in pick:
            pick_img=frame[yA:yB,xA:xB]
            result=self.capped(pick_img)
            if result==0:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
                self.capped_num+=1
            elif result==1:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 0, 255), 2)
                self.nocapped_num+=1
        return frame

    def StoreData(self,evt):
        if self.import_video_path=="":
            wx.MessageBox("请先导入视频","提示")
            return

        if len(self.db_info)==0:
            wx.MessageBox("请检查数据库设置","提示")
            return
        if self.table_name=="":
            wx.MessageBox("请先设置存储数据表","提示")
            return

        sqlconnect=pymysql.connect(host=self.db_info[0],user=self.db_info[3]
                                   ,port=int(self.db_info[1]),db=self.db_info[2],charset='utf8')
        if sqlconnect==False:
            wx.MessageBox("请检查数据库信息","出错")

        self.button3.SetLabel("正在写入...\n"
                              "时间较长,请耐心等待..")
        self.button3.Enabled(False)
        self.button1.Enabled(False)
        self.button2.Enabled(False)
        threading._start_new_thread(self.doStore,(sqlconnect,))

    def doStore(self,sqlconnect):
        cap = cv2.VideoCapture(self.import_video_path)
        nFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(nFrames)
        self.capped_num = 0
        self.nocapped_num = 0
        self.frame_num = nFrames
        for i in range(nFrames):
            ret, frame = cap.read()
            if i % 10 == 0:
                self.labeling(frame)

        cur = sqlconnect.cursor()
        try:
            filename = self.import_video_path.split('\\')[-1]
            print(filename)
            sql = "insert into %s " \
                  "(filename,capped,nocapped,frame_num) " \
                  "values ('%s',%d,%d,%d)" \
                  % (self.table_name, filename, self.capped_num, self.nocapped_num, self.frame_num)
            cur.execute(sql)
        finally:
            self.button3.SetLabel("写入当前数据")
            self.button3.Enabled(True)
            self.button1.Enabled(True)
            self.button2.Enabled(True)
            cur.close()
            sqlconnect.close()

    def LeadOut(self,evt):
        if len(self.db_info)==0:
            wx.MessageBox("未配置数据库，请先设置", "提示")
            return
        if self.table_name=="":
            wx.MessageBox("请先设置数据表","提示")
            return

        sqlconnect=pymysql.connect(host=self.db_info[0],user=self.db_info[3],
                                          passwd=self.db_info[4],port=int(self.db_info[1]),
                                          db=self.db_info[2],charset='utf8')
        if sqlconnect==False:
            wx.MessageBox("连接数据库出错，请检查", "提示")
            return

        cur=sqlconnect.cursor()
        sql="select * from %s"%self.table_name
        cur.execute(sql)
        result=cur.fetchall()
        if cur.rowcount == 0:
            wx.MessageBox("没有记录，无法导出", "提示")
            cur.close()
            sqlconnect.close()
            return
        try:
            import csv
            wildcard="*.csv"
            dlg=wx.FileDialog(self,"新建导出数据",os.getcwd(),"",wildcard,wx.FD_SAVE)
            if dlg.ShowModal()==wx.ID_OK:
                with open(dlg.GetPath(),'w') as csvfile:
                    wr=csv.writer(csvfile)
                    wr.writerow(['文件名','已戴帽数','未戴帽数','截止帧数'])
                    for each in result:
                        wr.writerow([items for items in each[1:]])
            wx.MessageBox("导出成功","提示")
        except:
            wx.MessageBox("出了一些状况，请检查数据库","提示")
        finally:
            cur.close()
            sqlconnect.close()

    def IsBeingDeleted(self):
        super(self).IsBeingDeleted(self)
        if self.import_video_father_path!="":
            os.remove(self.import_video_father_path+"\labeled_video.avi")

    #鉴别是否佩戴安全帽;
    def capped(self,pick):
        result= test(pick)
        if result==0:
            return 0
        elif result==1:
            return 1
        else:
            return 2

    def Destroy(self):
        if self.import_video_father_path != "":
            os.remove(self.import_video_father_path + "\labeled_video.avi")
        super(self).Destroy(self)

class Mydialog(wx.Dialog):
    def __init__(self,parent,title):
        super(Mydialog,self).__init__(parent=parent,title=title,size=(300,120))
        self.box=wx.BoxSizer(wx.VERTICAL)
        self.msg_panel=wx.Panel(self)
        self.msg_txt=wx.StaticText(self.msg_panel,label="正在处理...")
        self.cancel_panel=wx.Panel(self)
        self.cancel_btn=wx.Button(parent=self.cancel_panel,
                                  id=wx.ID_CANCEL,size=(55,30),pos=(220,10))
        self.box.Add(self.msg_panel,2,wx.ALL|wx.EXPAND)
        self.box.Add(self.cancel_panel,1,wx.ALL|wx.EXPAND)
        self.SetSizer(self.box)
        self.EnableCloseButton(False)

def getcontours(img):
    best_rate=2
    best_w=0
    best_h=0
    best_x=0
    best_y=0
    rate=1

    height=img.shape[0]
    width=img.shape[1]
    min_area=height*width/1000

    want_op=img.copy()
    want_op=cv2.cvtColor(want_op,cv2.COLOR_BGR2GRAY)
    ret,bina=cv2.threshold(want_op,0,255,cv2.THRESH_BINARY)
    _,contours,her=cv2.findContours(bina,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #连通区域，比例最接近，坐标限制；
    for contour in contours:
        area=cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        if x>width/5 and x<width*0.8 and y<height/4:
            if area > min_area:
                my_rate=w/h
                if abs(my_rate-rate)<abs(best_rate-rate):
                    best_rate=my_rate
                    best_h=h
                    best_w=w
                    best_x=x
                    best_y=y

    return best_x,best_y,best_w,best_h

def has_cap(bin_img,img):
    red_cap=[[110,220],[0,100],[0,100]]
    yellow_cap=[[205,255],[110,220],[0,100]]
    white_cap=[[205,255],[205,255],[205,255]]
    x,y,w,h=getcontours(bin_img)
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    area=(w-3)*(h-3)
    if w-3<=0 or h-3<=0:
        return 2
    #检测不到人头

    #轮廓线上左宽为2，下右宽为1;
    is_cap=np.zeros([h-3,w-3],np.int)
    print(str(h)+','+str(w))
    for i in range(y+2,y+h-1):
        print(' ')
        for j in range(x+2,x+w-1):
            bgr=img[i,j]
            print(bgr)
            if bgr[0]>=0 and bgr[0]<=100:
                if bgr[1]>=0 and bgr[1]<=100 and bgr[2]>=110 and bgr[2]<=220:
                    is_cap[i-y-2,j-x-2]=1
                elif bgr[1]>=110 and bgr[1]<=220 and bgr[2]>=205 and bgr[2]<=255:
                    is_cap[i-y-2,j-x-2]=1
            elif bgr[0]>=205 and bgr[0]<=255:
                if bgr[1]>=205 and bgr[1]<=255 and bgr[2]>=205 and bgr[2]<=255:
                    is_cap[i-y-2,j-x-2]=1
    area2=0
    for i in range(is_cap.shape[0]):
        for j in range(is_cap.shape[1]):
            area2+=is_cap[i,j]
    print(str(area)+','+str(area2))
    if area2/area>3/8:
        return 0
    else:
        return 1


Kl, Kh = 125, 188
Ymin, Ymax = 16, 235
Wlcb, Wlcr = 23, 20
Whcb, Whcr = 14, 10
Wcb, Wcr = 46.97, 38.76

# 椭圆模型参数
Cx, Cy = 109.38, 152.02
ecx, ecy = 1.60, 2.41
a, b = 25.39, 14.03
Theta = 2.53 / np.pi * 180

#高斯模型参数;
Mean=np.array([[117.4316],[148.5599]])
C=np.array([[97.0946,24.4700],[24.4700,141.9966]])
threshhold=0.22

which=1

def gethead(img):

    img_ycbcr=img.copy()
    img_bin=img.copy()
    img_ycbcr=cv2.cvtColor(img_ycbcr,cv2.COLOR_BGR2YCrCb)
    height=img_ycbcr.shape[0]
    width=img_ycbcr.shape[1]
    FaceProbImg = np.zeros([height, width])

    for y in range(height):
        for x in range(width):
            Y=img_ycbcr[y,x,0]
            CrY=img_ycbcr[y,x,1]
            CbY=img_ycbcr[y,x,2]
            Cb,Cr=Before_Model(Y,CbY,CrY)
            if which==1:
                #椭圆模型；
                ellipse=matrix_transform_and_getellipse(Cb,Cr)
                if ellipse<=1:
                    img_bin[y,x]=[255,255,255]
                else:
                    img_bin[y,x]=[0,0,0]
            elif which==2:
                #高斯模型；
                cbcr = np.array([[Cb], [Cr]])
                FaceProbImg[y, x] = np.exp(-0.5 * ((cbcr - Mean).T * np.linalg.inv(C) * (cbcr - Mean))[0, 0])
                if FaceProbImg[y, x] > threshhold:
                    img_bin[y, x] = [255,255,255]
                else:
                    img_bin[y,x]=[0,0,0]
            elif 3:
                #阈值判断；
                if Cb > 77 and Cb < 127 and Cr > 133 and Cr < 173:
                    img_bin[y,x]=[255,255,255]
                else:
                    img_bin[y,x]=[0,0,0]
            else:
                #椭圆模型；
                ellipse=ellipse2()
                cbcr=np.array([[Cb,Cr]])
                if ellipse[cbcr[0,0]]>0:
                    img_bin[y, x] = [255,255,255]
                else:
                    img_bin[y,x]=[0,0,0]

    return img_bin

def Before_Model(Y,CbY,CrY):
    if Y<Kl or Y>Kh:
        if Y<Kl:
            CbY_evr=108+(Kl-Y)*(118-108)/(Kl-Ymin)
            CrY_evr=154-(Kl-Y)*(154-144)/(Kl-Ymin)

            WcbY=Wlcb+(Y-Ymin)*(Wcb-Wlcb)/(Kl-Ymin)
            WcrY=Wlcr+(Y-Ymin)*(Wcr-Wlcr)/(Kl-Ymin)

        elif Y>Kh:
            CbY_evr=108+(Y-Kh)*(118-108)/(Ymax-Kh)
            CrY_evr=154+(Y-Kh)*(154-132)/(Ymax-Kh)

            WcbY=Whcb+(Ymax-Y)*(Wcb-Whcb)/(Ymax-Kh)
            WcrY=Whcr+(Ymax-Y)*(Wcr-Whcr)/(Ymax-Kh)

        CbKh_aver = 108 + (Kh - Kh) * (118 - 108) / (Ymax - Kh)
        CrKh_aver = 154 + (Kh - Kh) * (154 - 132) / (Ymax - Kh)

        Cb=(CbY-CbY_evr)*Wcb/WcbY+CbKh_aver
        Cr=(CrY-CrY_evr)*Wcr/WcrY+CrKh_aver
    else:
        Cb=CbY
        Cr=CrY
    return Cb,Cr

def matrix_transform_and_getellipse(Cb,Cr):
    costheta=np.cos(Theta)
    sintheta=np.sin(Theta)
    matrixA=np.array([[costheta,sintheta],[-sintheta,costheta]],np.double)
    matrixB=np.array([[Cb-Cx],[Cr-Cy]],np.double)
    matrixC=np.dot(matrixA,matrixB)
    x=matrixC[0,0]
    y=matrixC[1,0]
    ellipse=(x-ecx)**2/a**2+(y-ecy)**2/b**2
    return ellipse

def ellipse2():
    skincbcr=np.zeros([256,256],cv2.CV_8UC1)
    ellipse=cv2.ellipse(skincbcr,[113,155.6],[23.4,15.6],43.0,0.0,360.0,[255,255,255],-1)
    return ellipse

def test(test_image):
    bin_image=gethead(test_image)
    result= has_cap(bin_image, test_image)
    return result

def mytest():
    img=cv2.imread('C:\\Users\Dell\Desktop\detect_video\\20180623203109.png')
    bin_image=gethead(img)
    result= has_cap(bin_image, img)

base=wx.App(False)
frame=MainFrame()
base.MainLoop()


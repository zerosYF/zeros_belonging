import os
import threading
import winsound
from time import sleep

import cv2
import numpy as np
import pymysql
import pymysql.cursors
import wx
from imutils.object_detection import non_max_suppression

from my_detect.utils import mycap2


class MyFrame(wx.Panel):
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
                winsound.PlaySound("music/901028.wav",winsound.SND_FILENAME)
                self.doalert=False

    def labeling(self,frame):
        hog = cv2.HOGDescriptor()
        hog.load("utils/myHogDector1.bin")
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
        result= mycap2.test(pick)
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
import os
import threading

import cv2
import numpy as np
import pymysql
import pymysql.cursors
import wx
import wx.media
from imutils.object_detection import non_max_suppression

from my_detect.utils import mycap2


class MyFrame(wx.Panel):

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

        print(self.import_video_father_path)
        nFrames=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(nFrames)
        for i in range(nFrames):
            ret,frame=self.cap.read()
            if i%10==0:
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
            self.opr_dlg.EndModal(wx.ID_OK)
            wx.MessageBox("处理成功","成功");


    def labeling(self,frame):
        hog = cv2.HOGDescriptor()
        hog.load("utils/myHogDector1.bin")
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

        self.button3.SetLabel("正在写入...")
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
        result= mycap2.test(pick)
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

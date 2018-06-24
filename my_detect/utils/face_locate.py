import cv2
import numpy as np

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



import cv2
import numpy as np

from my_detect.utils import face_locate

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
    result= face_locate.has_cap(bin_image, test_image)
    return result

def mytest():
    img=cv2.imread('C:\\Users\Dell\Desktop\detect_video\\20180623203109.png')
    bin_image=gethead(img)
    result= face_locate.has_cap(bin_image, img)

#mytest()

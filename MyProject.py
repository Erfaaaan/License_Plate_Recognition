import sys
from PyQt5 import QtCore , QtGui , QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow,QLCDNumber,QSlider,QVBoxLayout
from skimage import io
from skimage import filters
from skimage.color import rgb2gray
import cv2
import imutils
import numpy as np
import pytesseract
import qimage2ndarray

class project(QMainWindow):
    def __init__(self):
        super(project , self).__init__()
        loadUi("1.ui" , self)
        
        self.openbtn.clicked.connect(self.openimage)
        self.detectbtn.clicked.connect(self.detection)
        self.scene=QtWidgets.QGraphicsScene()
        self.slider1.valueChanged.connect(self.updateLCD)
        self.slider2.valueChanged.connect(self.updateLCD2)

        

    def updateLCD(self,event):        
        self.lcd1.display(event)  
    def updateLCD2(self,event):        
        self.lcd2.display(event) 
    def openimage(self):
        global image
        fileName , _=QtWidgets.QFileDialog.getOpenFileName(self,'Open file','c:\\',"Image files (*.jpg *.gif)")
        image=io.imread(fileName)
        self.setimagetoscreen(image)
             
             
             
    def setimagetoscreen(self,img):
        SHAPE=img.shape
        x_pixel,y_pixel=SHAPE[0],SHAPE[1]
        self.scene.clear()
        pixmap=QtGui.QPixmap(qimage2ndarray.array2qimage(img))
        item=QtWidgets.QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)
        self.gv1.setScene(self.scene)
        self.gv1.fitInView(item , QtCore.Qt.IgnoreAspectRatio)
       
            
        
        
    def detection(self):
        global image
 

            # خواندن و تغییر اندازه ی عکس ها
        img = image
        img = imutils.resize(img, width=800)
            # تغییر رنگ (طوسی)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # فیلتر تاری (بلور)
        filtered = cv2.GaussianBlur(gray, (5, 5), 0)           
        #فیلتر کنی برای پیدا کردن مرز ها
        x1=self.lcd1.value()
        x2=self.lcd2.value()
        edged = cv2.Canny(filtered, x1, x2) 
            # پیدا کردن اشکال لبه دار بر اساس مرز های عکس
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # مرتب کردن اشکال لبه دار بر اساس مساحت آنها
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
        plate = False
        
        for c in contours:
                # پیدا کردن چند ضلعی های بسته از بین لبه ها (اشکال) یافت شده
            perimeter = cv2.arcLength(c, True)
                #پیدا کردن نقاط انحنا در چند ضلعی
            approx = cv2.approxPolyDP(c, 0.01 * perimeter, True)
                # شرط برای اینکه ببینیم شکل ما ۴ نقطه داشته باشد و مساحت آن به اندازه کافی بزرگ باشد
            if len(approx) == 4 and  cv2.contourArea(c) > 1000:
              
                    #دریافت یک نقطه از پلاک و طول و عرض آن
                x, y, w, h = cv2.boundingRect(c)
                    #اگر طول ما از ۲.۵ برابر عرض ما بزرگ تر و از ۴.۱ برابر آن کوچکتر بود
                if 2.5 < w / h < 4.1:
                   
                    plate = True
                        #جدا کردن پلاک تشخیص داده شده از عکس
                    cropped = img[y+5:y+h-5, x+5:x+w-5]   
                                        #نازک کردن کارکتر های عکس پلاک
                    kernel = np.ones((2,2), np.uint8)
                    img_dilation = cv2.dilate(cropped, kernel, iterations=1)
                        #تشخیص کارکتر های پلاک
                    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                    data = pytesseract.image_to_string(img_dilation, lang = 'eng', config = '-c page_separator=""')
                            #چک کردن اینکه آیا پلاک به درستی تشخیص داده شده یا خیر
                    if(data=='' or len(data)<4):
                        plate=False
                        continue
                    else:                                                
                        self.label.setText(data)    
                           #رسم مستطیل دور پلاک روی عکس اصلی                    
                        cv2.drawContours(img, c, -1, (0, 255, 0), 1)
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                        break
    
    
            # حال اگر همچنان پلاک را پیدا نکرده بودیم
        if not plate:
            for c in contours:
                perimeter = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.01 * perimeter, True)
                    # پیدا کردن اشکال بیش از ۴ ضلع که مساحتی حدود پلاک دارند و ممکن است سیستم آنرا تشخیص نداده باشد
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(c)
                    if 2.5 < w / h < 5.5 and 10500<=(w*h)<=22000:
                       
                        plate = True
                             #جدا کردن پلاک تشخیص داده شده از عکس
                        cropped = img[y+5:y+h-5, x+5:x+w-5]
                             #نازک کردن کارکتر های عکس پلاک
                        kernel = np.ones((2,2), np.uint8)
                        img_dilation = cv2.dilate(cropped, kernel, iterations=1)
                               #تشخیص کارکتر های پلاک
                        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                        data = pytesseract.image_to_string(img_dilation, lang = 'eng', config = '-c page_separator=""')
                            #چک کردن اینکه آیا پلاک به درستی تشخیص داده شده یا خیر
                        if(data=='' or len(data)<4):
                            plate=False
                            continue
                        else:                                                
                            self.label.setText(data)  
                                #رسم مستطیل دور پلاک روی عکس اصلی
                            cv2.drawContours(img, c, -1, (0, 255, 0), 1)
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                            break
                    
                           
    
        self.setimagetoscreen(img)    
      
      
           
            
app = QApplication(sys.argv)
welcome = project()
welcome.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")    
       
  

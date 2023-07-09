
from pickle import TRUE
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
#
from detectTracher import *
import numpy as np
import cv2

class VitesseApp(App):

    # fonction qui capture une image
    def capture(self,img,x,y,h,w,count1):
            crop_img = img[y-5:y + h+5, x-5:x + w+5]
            file = 'ImagesVoitures/' +str(count1) +'.jpg'
            cv2.imwrite(file, crop_img)

    # c'est le fonction principale de kivymd
    def build(self):
        self.icon="logo.png"
        layout=BoxLayout(orientation='vertical')
        self.image=Image(source='logo.png')
        layout.add_widget(self.image)
        
        StartCameraButton=Button(
            text="Démarrer",
            background_color = (1, 0, 1, 1), 
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(9,.1))

        StopCameraButton=Button(
            text="Arrêt",
            background_color = (0, 0, 1, 1), 
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(9,.1))

        layout.add_widget(StartCameraButton)
        layout.add_widget(StopCameraButton)
        StartCameraButton.bind(on_press = self.StartCamera)
        StopCameraButton.bind(on_press = self.StopCamera)
        
        return layout  
    
    # fonction qui active caméra ou une vidéo
    def StartCamera(self, event):
        self.tracker = EuclideanDistTracker()
    
        #  pour activer caméra
        # self.cap=cv2.VideoCapture(0)

        #  pour activer vidéo
        self.cap=cv2.VideoCapture("video.mp4")

        self.object_detector = cv2.createBackgroundSubtractorMOG2(history=80,varThreshold=25,detectShadows=True)
        self.capf = np.zeros(1000)

        Clock.schedule_interval(self.update, 1.0/33.0)

    
    # fonction qui désactive caméra ou une vidéo
    def StopCamera(self, event):
        self.cap=cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
    
    def update(self, dt):
        ret, self.frame = self.cap.read()
        roi=self.frame[200: 600 , 250:700]
        mask=self.object_detector.apply(roi)
        _,mask=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
        self.conturos,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.detections = []
        for cnt in self.conturos:
            area=cv2.contourArea(cnt)
            if area>500:  
                x,y,w,h=cv2.boundingRect(cnt)
                self.detections.append([x,y,w,h])
        boxes_ids = self.tracker.update(self.detections)
        for box_id in boxes_ids:
            x,y,w,h,id = box_id
            if(y >= 200 and y<225):
                if(self.capf[id]==0):
                    self.capf[id] = 1 
                    self.capture(roi,x,y,h,w,id)
                   
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv2.putText(roi,str(id),(x,y-15), cv2.FONT_HERSHEY_PLAIN,1,(255,255,0),2)
            
        cv2.line(roi, (100, 100), (460, 100), (0, 160, 255), 2)
        cv2.line(roi, (0, 335), (960, 335), (0, 0, 255), 2)
        
        cv2.imshow("roi",roi)
        cv2.imshow("mask",mask)

        self.image_frame=self.frame
        buffer = cv2.flip(self.frame, 0).tostring()
        texture1 = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')  
        texture1.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture1 

    
if __name__ == '__main__':
    VitesseApp().run()
    
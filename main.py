# Untitled - By: sqgg刘俊麟 - 周一 9月 28 2020
import sensor, image, time
import sensor, image, time, math
from pyb import UART
import json
import ustruct
import pyb
from pyb import Pin

red_threshold=(13, 66, 22, 81, 13, 73)
area=(0,0,280,160)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(20)
sensor.set_auto_whitebal(False)
#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡
sensor.set_auto_gain(False) # must be turned off for color tracking
clock = time.clock()

uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters
p_out = Pin('P7', Pin.OUT_PP)#设置p_out为输出引脚

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


def find_maxball(ball_threshold,area):
    pass
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([ball_threshold],roi=area)
    print(blobs)
    if blobs:
        max_blob = find_max(blobs)
        img.draw_rectangle(max_blob[0:4]) # rect
        img.draw_cross(max_blob[5], max_blob[6]) # cx, cy
        return(max_blob)



def track_maxball(red_threshold,area):
    track=find_maxball(red_threshold,area)
    if track:
        #print('track=',track)
        x1=track[0]-2
        y1=track[1]-2
        w1=track[2]+4
        h1=track[3]+4
        area=(x1,y1,w1,h1)
        #print('area=',area,area[1])
    else:
        print('跳出范围了')
        area=(0,0,160,120)
    return(track)
    print("帧率 : ",clock.fps())
    

def sending_data(cx,cy):
    global uart;
    #frame=[0x2C,18,cx%0xff,int(cx/0xff),cy%0xff,int(cy/0xff),0x5B];
    #data = bytearray(frame)
    data = ustruct.pack("<bbhhb",              #格式为俩个字符俩个短整型(2字节)
                   0x2C,                       #帧头1
                   0x12,                       #帧头2
                   int(cx), # up sample by 4    #数据1
                   int(cy), # up sample by 4    #数据2
                   0x5B)
    uart.write(data);   #必须要传入一个字节数组

    
    
p_out.low()#设置p_out引脚为低
#mainloop
while(True):
    for i in range(10):
        track=find_maxball(red_threshold,area)
    if track!=None:
        print('找到了最大小球，追踪最大小球')
        p_out.low()#设置p_out引脚为高
        while(True):

            #print(track)

            x1=track[0]-2
            y1=track[1]-2
            w1=track[2]+4
            h1=track[3]+4
            area=(x1,y1,w1,h1)
            print('area=',area)
            while(True):
                clock.tick() # Track elapsed milliseconds between snapshots().
                img = sensor.snapshot() # Take a picture and return the image.
                blobs = img.find_blobs([red_threshold],roi=area)
                cx=0;cy=0;

                if blobs:
                max_b = find_max(blobs);

                    for b in blobs:
                        x1=b[0]-4
                        y1=b[1]-4
                        w1=b[2]+8
                        h1=b[3]+8
                        area=(x1,y1,w1,h1)

                        print('area=',area)
                        print('成功追踪',b)
                        img.draw_rectangle(area[0:4]) # rect
                        img.draw_rectangle(b[0:4]) # rect
                        cx=max_b[5];
                        cy=max_b[6];
                        img.draw_line((160,120,cx,cy), color=(127));
                        #img.draw_string(160,120, "(%d, %d)"%(160,120), color=(127));
                        img.draw_string(cx, cy, "(%d, %d)"%(cx,cy), color=(127));

                    sending_data(cx,cy); #发送点位坐标
                    recive_data();

                else:
                    print('丢失目标')
                    area=(0,0,160,120)
    else:
        print('没找着,继续找最大')

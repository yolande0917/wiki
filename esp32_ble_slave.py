import gc
import sys
import network as n
import gc
import time
from machine import Pin
led=Pin(2,Pin.OUT)
LEDVALUE = 0
b = n.Bluetooth()
#设置DFB1和DFB2的默认值
DFB1Value = '1'
DFB2Value = '2'


'''定义蓝牙事件的回调函数。连接事件的回调,蓝牙被连接和被断开会调用这个事件回调'''  
def bcb(b,e,d,u):
  if e == b.CONNECT:
    print("CONNECT")
  elif e == b.DISCONNECT:
    print("DISCONNECT")
    #被断开连接后继续开始广播
    b.ble_settings(adv_man_name = "DFRobot", adv_dev_name="firebeetle-esp32")
    b.ble_adv_enable(True)
  else:
    print ('Unknown event', e,d)
    
'''定义蓝牙接收数据的回调函数,蓝牙接收到数据，或则被读取数据时会调用这个回调''' 
def cb (cb, event, value, userdata):
  global DFB1Value
  global DFB2Value
  global LEDVALUE
  if event == b.READ:
    if userdata == 'DFB1':#读取DFB1的特征值，返回1
      return DFB1Value
    elif userdata == 'DFB2':
      return DFB2Value
  elif event == b.WRITE:#如果接收到了write的数据会打印出接收到的值
    if userdata == 'DFB1':
      DFB1Value = value#更改DFB1的值
      led.value(1)
      print ('From 0xDFB1', value)
    elif userdata == 'DFB2':
      DFB2Value = value#更改DFB2的值
      print ('From 0xDFB2', value)
    if LEDVALUE is 0:
      LEDVALUE = 1
    else:
      LEDVALUE = 0
    led.value(LEDVALUE)
 
 
def gatts():
  #创建一个Service uuid为0xDFB0的Service
  s1 = b.Service(0xDFB0)
  #给刚刚创建的DFB0的Service创建两个Characteristic分别为0xDFB1和0xDFB2
  c1 = s1.Char(0xDFB1)
  c2 = s1.Char(0xDFB2)
  
  #分别给两个Characteristic设置回调及它们回调函数的userdata名分别为DFB1和DFB2
  c1.callback(cb, 'DFB1')
  c2.callback(cb, 'DFB2')
 
  #启动刚刚创建的DFB0的Service.
  s1.start()
  
  #设置它的厂商名字为DFRobot,广播名字为firebeetle-esp32  
  b.ble_settings(adv_man_name = "DFRobot", adv_dev_name="firebeetle-esp32")
  #开始广播
  b.ble_adv_enable(True)
  
#设置蓝牙的事件回调
b.callback(bcb)

gatts()
while(True):
  pass

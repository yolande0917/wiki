import gc
import sys
import network as n
import gc
import time
from machine import Pin
button = Pin(16, Pin.IN)
 
b = n.Bluetooth()
mychar = None
found = {}
complete = True
connectname = ""
mac=b'\x00\x00\x00\x00\x00\x00'
'''定义注册蓝牙事件的回调函数。连接事件，搜索事件的回调'''
def bcb(b,e,d,u):
  global complete
  global found
  global connectname
  global mac
  if e == b.CONNECT:
        print("CONNECT")
  elif e == b.DISCONNECT:
        print("DISCONNECT")
  elif e == b.SCAN_RES:
    '''搜索完成时检测是否搜索到需要连接的设备'''
    if complete:
      found = {}
      adx, name,ssic= d
      if connectname == str(name):
        mac = adx
        print(d)
        if adx not in found:
          found[adx] = name
      else:
        print('else')
        print(d)
 
  elif e == b.SCAN_CMPL:
    '''搜索时打印搜索到的设备信息'''
    ok = True
    print("Scan Complete")
    complete = True
    print ('\nFinal List:')
    for adx, name in found.items():
      print ('Found:' + ':'.join(['%02X' % i for i in adx]), name)
      print('connect ',name)
  else:
    print ('Unknown event', e,d)
    
'''定义蓝牙接收数据的回调函数'''
def cb (cb, event, value, userdata):
  print('charcb ', cb, userdata, ' ', end='')
  if event == b.READ:  
    return 'ABCDEFG'
  elif event == b.WRITE:
    print ('Write', value)
  elif event == b.NOTIFY:
    print ('Notify', value)
    
'''定义蓝牙的连接函数'''    
def conn(bda):
  global mychar
  '''蓝牙连接其必须关掉搜索模式'''
  b.ble_settings(adv_is_scan_rsp = False)
  conn = b.connect(bda)
  i=0
  while not conn.is_connected():
    i=i+1
    time.sleep(2) # Wait for services
    '''检测是否有0xDFB0这个Service'''
    service = ([s for s in conn.services() if s.uuid()[0:4] == b'\x00\x00\xDF\xB0'] + [None])[0]
    if service:
      '''检测0xDFB0这个Service里是否有0xDFB1这个Char'''
      char = ([c for c in service.chars() if c.uuid()[0:4] == b'\x00\x00\xDF\xB1'] + [None])[0]
      mychar = char
      if char:
        '''注册0xDFB1的数据回调函数'''
        char.callback(cb)
    if i == 10:
      print('time out')
      break
  return conn
  
def set_connetname(name):
  return "b'%s'" % name
  
def scan():
  global connectname
  '''设置需要连接的蓝牙设备'''
  connectname = set_connetname("firebeetle-esp32")
  '''设置其为搜索模式'''
  b.ble_settings(adv_is_scan_rsp = True)
  b.scan_start(5)
  time.sleep(10)
'''注册蓝牙事件的回调'''
b.callback(bcb)
'''开始搜索'''
scan()
print('mac:',mac)
'''开始连接'''
conn(mac)
while True:
  if button.value() == 1:
    mychar.write("hello")
  time.sleep(1)

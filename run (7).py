import json
import time
import RPi.GPIO as GPIO
import aliLink
import paho.mqtt.client as mqttd
import rpi
from dht11 import MyDHT11

GPIO.setmode(GPIO.BCM)
soilpin = 16  # 土壤传感器引脚号
GPIO.setup(soilpin, GPIO.IN)  # 设置为输入模式
mDht11 = MyDHT11(26)  # DHT11传感器引脚号

# 三元素（iot后台获取）
ProductKey = 'k1yxxmXRmf9'
DeviceName = 'raspberrypi_test1'
DeviceSecret = "c4bea3903abaf35ca37c8138c1f281ca"

# topic (iot后台获取)
POST = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/event/property/post'  # 上报消息到云
POST_REPLY = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/event/property/post_reply'
SET = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/service/property/set'  # 订阅云端指令

# 状态变量，用于控制感应器
sensors_active = True

def activate_sensors():
    global sensors_active
    sensors_active = True
    print("Sensors activated.")

def deactivate_sensors():
    global sensors_active
    sensors_active = False
    print("Sensors deactivated.")

# 消息回调函数
def on_message(client, userdata, msg):
    global sensors_active
    try:
        Msg = json.loads(msg.payload)
        signal = Msg['params'].get('signal')
        switch = Msg['params'].get('PowerLed')
        if signal == '#3':
            activate_sensors()
        elif signal == '#4':
            deactivate_sensors()
        if switch is not None:
            rpi.powerLed(switch)
    except Exception as e:
        print("Error handling message:", e)
    print("Received message:", msg.payload)

# 连接回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe(SET)  # 订阅服务器下发消息topic
    else:
        print(f"Connection failed with code {rc}")

# 链接信息
Server, ClientId, userName, Password = aliLink.linkiot(DeviceName, ProductKey, DeviceSecret)

# MQTT 客户端初始化
client = mqttd.Client()
client.username_pw_set(userName, Password)
client.on_message = on_message
client.on_connect = on_connect
client.connect(Server, 1883, 60)
client.loop_start()  # 开启后台循环

while True:  # 10秒检测一次
    time.sleep(10)

    # 读取传感器数据
    dht11_temp, dht11_humi = mDht11.read_dht11()
    if dht11_temp is None or dht11_humi is None:
        print("Failed to read from DHT11 sensor.")
        continue
    soil_humi = GPIO.input(soilpin)

    print("Temperature is", dht11_temp, "C\nHumidity is", dht11_humi, "%")

    # 根据温度发送信号
    if dht11_temp > 30:
        print("Temperature above 30, sending signal #1")
        client.publish(POST, json.dumps({'signal': '#1'}))
    elif dht11_temp <= 30:
        print("Temperature 30 or below, sending signal #2")
        client.publish(POST, json.dumps({'signal': '#2'}))

    # 构建与云端模型一致的消息结构
    updateMsn = {
        'dht11temp': dht11_temp,
        'dht11humi': dht11_humi,
        'soilhumi': soil_humi
    }
    JsonUpdataMsn = aliLink.Alink(updateMsn)
    print(JsonUpdataMsn)

    # 如果传感器处于激活状态，则上报数据
    if sensors_active:
        client.publish(POST, JsonUpdataMsn)

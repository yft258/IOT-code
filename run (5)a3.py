import json
import time
import RPi.GPIO as GPIO
import aliLink
import mqttd
import rpi
from dht11 import MyDHT11

GPIO.setmode(GPIO.BCM)
soilpin = 16  # 土壤传感器引脚号(Soil Sensor Pin Number)
GPIO.setup(soilpin, GPIO.IN)  # 设置为输入模式(Set to input mode)
mDht11 = MyDHT11(26)  # DHT11传感器引脚号(DHT11 Sensor Pin Number)

# 三元素（iot后台获取）(Need information from Alibaba Cloud Services)
ProductKey = 'k1yxxmXRmf9'
DeviceName = 'raspberrypi_test1'
DeviceSecret = "c4bea3903abaf35ca37c8138c1f281ca"

# topic (iot后台获取)
POST = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/event/property/post'  # 上报消息到云(Reporting messages to the cloud)
POST_REPLY = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/event/property/post_reply'
SET = '/sys/k1yxxmXRmf9/raspberrypi_test1/thing/service/property/set'  # 订阅云端指令(Subscribe to Cloud Commands)

# 状态变量，用于控制感应器（use to control sensors）
sensors_active = True  # 初始状态为读取数据(Initial state is reading data)

def activate_sensors():
    global sensors_active
    sensors_active = True
    print("Sensors activated.")

def deactivate_sensors():
    global sensors_active
    sensors_active = False
    print("Sensors deactivated.")

# 消息回调函数(message callback function)
def on_message(client, userdata, msg):
    global sensors_active
    try:
        Msg = json.loads(msg.payload)
        signal = Msg['params'].get('signal')
        switch = Msg['params'].get('PowerLed')
        if signal == '#3':
            deactivate_sensors()
        elif signal == '#4':
            activate_sensors()
        if switch is not None:
            rpi.powerLed(switch)
    except Exception as e:
        print("Error handling message:", e)
    print("Received message:", msg.payload)

# 连接回调函数(connection callback function)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print(f"Connection failed with code {rc}")

# 链接信息(link information)
Server = 'iot-06z01hca7lnlv19.mqtt.iothub.aliyuncs.com'
ClientId = 'k1yxxmXRmf9.raspberrypi_test1|securemode=2,signmethod=hmacsha256,timestamp=1734068438346|'
userName = 'raspberrypi_test1&k1yxxmXRmf9'
Password = '7d4bef27104db096e2b2dd91ebfac71eb500f5f3339edbef0390ec4cfef5ec4a'

# 链接信息
Server, ClientId, userName, Password = aliLink.linkiot(DeviceName, ProductKey, DeviceSecret)


# mqtt链接(mqtt link)
mqtt = mqttd.MQTT(Server, ClientId, userName, Password)
mqtt.subscribe(SET)  # 订阅服务器下发消息topic
mqtt.begin(on_message, on_connect)

#mqtt_hlink
def mqtt_connect():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("hlink.space", 1883)
    client.subscribe("LYK114514")
    client.loop_forever()

while True:  # 10秒检测一次(test one time every 10s)
    time.sleep(10)

    # 只在传感器启用状态下读取数据(Reads data only when sensor is enabled)
    if sensors_active:
        # 读取传感器数据(Reading sensor data)
        dht11_temp, dht11_humi = mDht11.read_dht11()
        soil_humi = GPIO.input(soilpin)

        print("Temperature is", dht11_temp, "C\nHumidity is", dht11_humi, "%")

        # 根据温度发送信号(Sends signals according to temperature)
        if dht11_temp > 30:
            print("Temperature above 30, sending signal #1")
            mqtt.push(POST, json.dumps({'signal': '#1'}))
        elif dht11_temp <= 30:
            print("Temperature 30 or below, sending signal #2")
            mqtt.push(POST, json.dumps({'signal': '#2'}))

        # 构建与云端模型一致的消息结构(Build a message structure that is consistent with the cloud model)
        updateMsn = {
            'dht11temp': dht11_temp,
            'dht11humi': dht11_humi,
            'soilhumi': soil_humi
        }
        JsonUpdataMsn = aliLink.Alink(updateMsn)
        print(JsonUpdataMsn)

        # 上报数据(report data)
        mqtt.push(POST, JsonUpdataMsn)

def send_mqtt_message(message):
    client = mqtt.Client()
    client.connect("hlink.space", 1883, 60)
    client.publish("LYK114514", message)
    client.disconnect()

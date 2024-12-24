import RPi.GPIO as GPIO
import time

class MyDHT11():
    def __init__(self, pin=18):
        self.history_humidity = 0
        self.history_temperature = 0

        self.tmp = []  # 用来存放读取到的数据
        self.data = pin  # DHT11的data引脚连接到的树莓派的GPIO引脚，使用BCM编号
        self.a, b = 0, 0


    def delayMicrosecond(self, t):  # 微秒级延时函数
        start, end = 0, 0  # 声明变量
        start = time.time()  # 记录开始时间
        t = (t - 3) / 1000000  # 将输入t的单位转换为秒，-3是时间补偿
        while end - start < t:  # 循环至时间差值大于或等于设定值时
            end = time.time()  # 记录结束时间

    def DHT11(self):
        GPIO.setup(self.data, GPIO.OUT)  # 设置GPIO口为输出模式
        GPIO.output(self.data, GPIO.HIGH)  # 设置GPIO输出高电平
        self.delayMicrosecond(10 * 1000)  # 延时10毫秒
        GPIO.output(self.data, GPIO.LOW)  # 设置GPIO输出低电平
        self.delayMicrosecond(25 * 1000)  # 延时25毫秒
        GPIO.output(self.data, GPIO.HIGH)  # 设置GPIO输出高电平
        GPIO.setup(self.data, GPIO.IN)  # 设置GPIO口为输入模式
        a = time.time()  # 记录循环开始时间
        while GPIO.input(self.data):  # 一直循环至输入为低电平
            b = time.time()  # 记录结束时间
            if (b - a) > 0.1:  # 判断循环时间是否超过0.1秒，避免程序进入死循环卡死
                break  # 跳出循环

        a = time.time()
        while GPIO.input(self.data) == 0:  # 一直循环至输入为高电平
            b = time.time()
            if (b - a) > 0.1:
                break

        a = time.time()
        while GPIO.input(self.data):  # 一直循环至输入为低电平
            b = time.time()
            if (b - a) >= 0.1:
                break

        for i in range(40):  # 循环40次，接收温湿度数据
            a = time.time()
            while GPIO.input(self.data) == 0:  # 一直循环至输入为高电平
                b = time.time()
                if (b - a) > 0.1:
                    break
            self.delayMicrosecond(28)  # 延时28微秒

            if GPIO.input(self.data):  # 超过28微秒后判断是否还处于高电平
                self.tmp.append(1)  # 记录接收到的bit为1

                a = time.time()
                while GPIO.input(self.data):  # 一直循环至输入为低电平
                    b = time.time()
                    if (b - a) > 0.1:
                        break
            else:
                self.tmp.append(0)  # 记录接收到的bit为0


    def read_dht11(self):
        GPIO.setmode(GPIO.BCM)  # 设置为BCM编号模式
        GPIO.setwarnings(False)
        del self.tmp[0:]  # 删除列表  # 延时1秒
        self.DHT11()

        humidity_bit = self.tmp[0:8]  # 分隔列表，第0到7位是湿度整数数据
        humidity_point_bit = self.tmp[8:16]  # 湿度小数
        temperature_bit = self.tmp[16:24]  # 温度整数
        temperature_point_bit = self.tmp[24:32]  # 温度小数
        check_bit = self.tmp[32:40]  # 校验数据

        humidity_int = 0
        humidity_point = 0
        temperature_int = 0
        temperature_point = 0

        check = 0
        for i in range(8):  # 二进制转换为十进制
            humidity_int += humidity_bit[i] * 2 ** (7 - i)
            humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
            temperature_int += temperature_bit[i] * 2 ** (7 - i)
            temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
            check += check_bit[i] * 2 ** (7 - i)

        humidity = humidity_int + humidity_point / 10
        temperature = temperature_int + temperature_point / 10

        check_tmp = humidity_int + humidity_point + temperature_int + temperature_point

        if check == check_tmp and temperature != 0 and temperature != 0:  # 判断数据是否正常
            self.history_humidity = humidity
            self.history_temperature = temperature
        return self.history_temperature, self.history_humidity

if __name__ == "__main__":
    mDht11 = MyDHT11(18)
    while True:
        t, h = mDht11.read_dht11()
        print(t, h)
        time.sleep(3)
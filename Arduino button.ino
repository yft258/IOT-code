#include <WiFi.h>
#include <PubSubClient.h>

// WiFi 配置信息
const char* ssid = "HUAWEImate15plus";
const char* password = "ABCD1234";

// MQTT 服务器信息
const char* mqtt_server = "hlink.space";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
// 按钮引脚
const int button1Pin = 12; // 修改为直接使用数字

void setup_wifi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() { // 修正拼写错误
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ARDUINO114514")) { // 去掉空格
      Serial.println("connected");
      client.subscribe("LYK114514");  // 替换为订阅的主题
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 10 seconds");
      delay(10000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // 设置按钮引脚为输入模式
  pinMode(button1Pin, INPUT_PULLUP);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();

  // 按钮 1 逻辑
  int button1State = digitalRead(button1Pin);
  if (button1State == LOW) {
    Serial.println("press");
    delay(100);
    while (digitalRead(button1Pin) == LOW) {
      Serial.println("press");
      delay(10);
    }
    client.publish("LYK114514", "#1");
    Serial.println("Button 1 pressed, sent #1");
  }
}

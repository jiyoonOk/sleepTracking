# MQTT 통신 및 센서 데이터 처리
import time
import paho.mqtt.client as mqtt
import circuit 

def on_connect(client, userdata, flag, rc, prop=None):
	client.subscribe("led/white")
	client.subscribe("led/yellow")
	client.subscribe("servo/humidifier")
	client.subscribe("servo/fan")
	client.subscribe("request/temperature")
	client.subscribe("request/humidity")
	client.subscribe("request/light")
	print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
	topic = msg.topic
	payload = msg.payload.decode()
	print(f"DEBUG - Received message: {payload} on topic: {topic}")
	
	# 초기 상태값 요청 처리
	if topic == "request/temperature":
		temperature, _ = circuit.measure_temperature_humidity()
		if temperature is not None:
			client.publish("temperature", temperature)
	elif topic == "request/humidity":
		_, humidity = circuit.measure_temperature_humidity()
		if humidity is not None:
			client.publish("humidity", humidity)
	elif topic == "request/light":
		light = circuit.measure_light()
		client.publish("light", light)
	# 기존 코드는 그대로 유지
	elif topic == "led/white":
		brightness = int(payload)
		circuit.controlLED("white", brightness)
	elif topic == "led/yellow":
		brightness = int(payload)
		circuit.controlLED("yellow", brightness)
	elif topic == "servo/humidifier":
		angle = 180 if payload == "1" else 0
		circuit.control_servo(angle)
	elif topic == "servo/fan":
		angle = 180 if payload == "1" else 0
		circuit.control_servo(angle)

ip = "172.20.10.5"  # localhost 대신 실제 브로커 IP 사용

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
	client.connect(ip, 1883)
	client.loop_start()
	
	while True:
		try:
			distance = circuit.measure_distance()
			temperature, humidity = circuit.measure_temperature_humidity()
			light = circuit.measure_light()
			
			client.publish("ultrasonic", distance)
			if temperature is not None and humidity is not None:
				client.publish("temperature", temperature)
				client.publish("humidity", humidity)
			client.publish("light", light)
			
			time.sleep(0.5)
		except Exception as e:
			print(f"Error reading sensors: {e}")
			time.sleep(1)
			
except KeyboardInterrupt:
	print("프로그램 종료")
	circuit.cleanup()
	client.loop_stop()
	client.disconnect()

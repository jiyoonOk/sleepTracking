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
	current_time = time.strftime("%H:%M:%S")
	print(f"[{current_time}] 메시지 수신: {payload} (토픽: {topic})")
	
	# 초기 상태값 요청 처리
	if topic == "request/temperature" or topic == "request/humidity":
		temperature, humidity = circuit.measure_temperature_humidity()
		if temperature is not None and humidity is not None:
			client.publish("temperature", f"{temperature:.1f}")
			client.publish("humidity", f"{humidity:.1f}")
			print(f"[{current_time}] 온습도 발행: {temperature:.1f}°C, {humidity:.1f}%")
	elif topic == "request/light":
		light = circuit.measure_light()
		if light is not None:
			client.publish("light", light)
			print(f"[{current_time}] 조도 발행: {light}%")
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
			current_time = time.strftime("%H:%M:%S")
			print(f"\n[{current_time}] === 센서 측정 시작 ===")
			
			# 온습도 측정 및 발행
			temperature, humidity = circuit.measure_temperature_humidity()
			if temperature is not None and humidity is not None:
				client.publish("temperature", f"{temperature:.1f}")
				client.publish("humidity", f"{humidity:.1f}")
				print(f"[{current_time}] 온습도 발행 완료: {temperature:.1f}°C, {humidity:.1f}%")
			else:
				print(f"[{current_time}] 온습도 측정 실패")
			
			# 나머지 센서 측정 및 발행
			distance = circuit.measure_distance()
			if distance is not None:
				client.publish("ultrasonic", distance)
				print(f"[{current_time}] 거리 발행: {distance}cm")
			
			light = circuit.measure_light()
			if light is not None:
				client.publish("light", light)
				print(f"[{current_time}] 조도 발행: {light}%")
			
			print(f"[{current_time}] === 센서 측정 완료 ===")
			time.sleep(0.2)
			
		except Exception as e:
			print(f"[{current_time}] 에러 발생: {str(e)}")
			print(f"[{current_time}] 에러 타입: {type(e).__name__}")
			time.sleep(1)
			
except KeyboardInterrupt:
	print("프로그램 종료")
	circuit.cleanup()
	client.loop_stop()
	client.disconnect()

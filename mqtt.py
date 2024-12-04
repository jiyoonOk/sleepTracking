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
		power = int(payload)
		circuit.control_humidifier(power)
	elif topic == "servo/fan":
		power = int(payload)
		circuit.control_fan(power)

ip = "172.20.10.5"  # localhost 대신 실제 브로커 IP 사용

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
	print(f"브로커 연결 시도: {ip}")
	client.connect(ip, 1883)
	client.loop_start()
	print("MQTT 연결 성공!")
	
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
			
			# 초음파 센서 측정 및 발행
			distance = circuit.measure_distance()
			if distance is not None:
				client.publish("ultrasonic", str(distance))
				print(f"[{current_time}] 거리 발행: {distance}cm")
			
			# 조도 측정 및 발행
			light = circuit.measure_light()
			if light is not None:
				client.publish("light", str(light))
				print(f"[{current_time}] 조도 발행: {light}%")
			
			print(f"[{current_time}] === 센서 측정 완료 ===")
			time.sleep(0.2)  # 1초 간격으로 측정
			
		except Exception as e:
			print(f"[{current_time}] 센서 측정 중 에러 발생: {str(e)}")
			print(f"[{current_time}] 에러 타입: {type(e).__name__}")
			time.sleep(0.2)
			continue  # 에러가 발생해도 계속 실행

except KeyboardInterrupt:
	print("\n프로그램 종료")
	# 모든 장치 끄기
	circuit.control_humidifier(0)  # 가습기 끄기
	circuit.controlLED("white", 0)  # 흰색 LED 끄기
	circuit.controlLED("yellow", 0)  # 노란색 LED 끄기
	circuit.control_fan(0)  # 선풍기 끄기
	circuit.cleanup()  # GPIO 정리
	client.loop_stop()
	client.disconnect()

except Exception as e:
	print(f"예기치 않은 오류: {str(e)}")
	# 여기서도 장치들을 끄고 정리
	circuit.control_humidifier(0)
	circuit.controlLED("white", 0)
	circuit.controlLED("yellow", 0)
	circuit.control_fan(0)
	circuit.cleanup()
	client.loop_stop()
	client.disconnect()

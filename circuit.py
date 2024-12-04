# 센서 및 하드웨어 제어 코드
import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio
import threading

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# I2C 설정 (온습도 센서용)
sda = 2  # GPIO2 핀
scl = 3  # GPIO3 핀
i2c = busio.I2C(scl, sda)
sensor = HTU21D(i2c)  # HTU21D 온습도 센서 객체

# 조도 센서 설정 (MCP3008 ADC)
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

# LED 설정
LED_WHITE = 5
LED_YELLOW = 6
GPIO.setup(LED_WHITE, GPIO.OUT)
GPIO.setup(LED_YELLOW, GPIO.OUT)

# LED PWM 객체 전역 설정
led_white_pwm = GPIO.PWM(LED_WHITE, 100)
led_yellow_pwm = GPIO.PWM(LED_YELLOW, 100)
led_white_pwm.start(0)
led_yellow_pwm.start(0)

# 스위치 설정
SWITCH = 21
GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 초음파 센서 설정
TRIG = 20
ECHO = 16
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 선풍기용 서보모터 설정
SERVO_FAN = 12  # GPIO 12번 핀 사용
GPIO.setup(SERVO_FAN, GPIO.OUT)
fan_pwm = GPIO.PWM(SERVO_FAN, 50)  # 50Hz PWM
fan_pwm.start(0)

# DC 모터 설정 (가습기용)
HUMIDIFIER = 26
GPIO.setup(HUMIDIFIER, GPIO.OUT)

# 전역 변수로 선풍기 상태 추가
fan_running = False
fan_thread = None

def measure_light():
    """조도 센서 값 읽기 (0-100%)"""
    try:
        current_time = time.strftime("%H:%M:%S")
        print(f"\n[{current_time}] 조도 센서 측정 시작")
        
        adc_value = mcp.read_adc(0)
        if adc_value is None:
            print(f"[{current_time}] 조도 센서 읽기 실패: ADC 값이 None")
            return None
            
        light_percentage = (adc_value / 1023.0) * 100.0
        print(f"[{current_time}] 측정 성공 - ADC값: {adc_value}, 조도: {light_percentage}%")
        return round(light_percentage, 2)
        
    except Exception as e:
        print(f"[{current_time}] 조도 센서 에러: {str(e)}")
        print(f"[{current_time}] 에러 타입: {type(e).__name__}")
        return None

def getTemperature(sensor):
    """센서로부터 온도 값 수신 함수"""
    temp = float(sensor.temperature)
    print(f"현재 온도는 {temp:.1f}°C")
    return temp

def getHumidity(sensor):
    """센서로부터 습도 값 신 함수"""
    humid = float(sensor.relative_humidity)
    print(f"현재 습도는 {humid:.1f}%")
    return humid

def measure_temperature_humidity():
    """온습도 센서 값 읽기"""
    try:
        current_time = time.strftime("%H:%M:%S")
        print(f"\n[{current_time}] === 온습도 센서 측정 시작 ===")
        
        temperature = getTemperature(sensor)
        humidity = getHumidity(sensor)
        
        print(f"[{current_time}] === 온습도 센서 측정 완료 ===")
        return temperature, humidity
        
    except Exception as e:
        print(f"[{current_time}] 온습도 센서 에러: {str(e)}")
        print(f"[{current_time}] 에러 타입: {type(e).__name__}")
        return None, None

def measure_distance():
    """초음파 센서로 거리 측정"""
    try:
        GPIO.output(TRIG, False)
        time.sleep(0.5)
        
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        return distance
    except Exception as e:
        print(f"거리 측정 에러: {str(e)}")
        return None

def controlLED(led_type, brightness):
    """LED 제어 (PWM)"""
    try:
        brightness = float(brightness)  # 문자열을 숫자로 변환
        print(f"DEBUG - LED control: type={led_type}, brightness={brightness}")  # 상세 로그 추가
        
        if led_type == "white":
            led_white_pwm.ChangeDutyCycle(brightness)
            print(f"DEBUG - White LED duty cycle set to {brightness}")  # 상세 로그 추가
        else:
            led_yellow_pwm.ChangeDutyCycle(brightness)
            print(f"DEBUG - Yellow LED duty cycle set to {brightness}")  # 상세 로그 추가
    except Exception as e:
        print(f"LED control error: {e}")

def fan_rotation():
    """선풍기 회전 함수 - 별도 스레드에서 실행"""
    global fan_running
    while fan_running:
        # 0도에서 180도까지
        for angle in range(0, 180, 5):
            if not fan_running:
                break
            duty = (angle / 18.0) + 2.5
            fan_pwm.ChangeDutyCycle(duty)
            time.sleep(0.05)
        # 180도에서 0도까지
        for angle in range(180, 0, -5):
            if not fan_running:
                break
            duty = (angle / 18.0) + 2.5
            fan_pwm.ChangeDutyCycle(duty)
            time.sleep(0.05)

def control_fan(power):
    """선풍기(서보모터) 제어 함수
    power: 1이면 켜짐(연속 회전), 0이면 꺼짐
    """
    global fan_running, fan_thread
    
    try:
        if power == 1:
            # 선풍기 켜기
            fan_running = True
            fan_thread = threading.Thread(target=fan_rotation)
            fan_thread.daemon = True  # 메인 프로그램 종료시 스레드도 종료
            fan_thread.start()
        else:
            # 선풍기 끄기
            fan_running = False
            if fan_thread:
                fan_thread.join(timeout=1)  # 스레드 종료 대기
            fan_pwm.ChangeDutyCycle(2.5)  # 0도
            time.sleep(0.5)
            fan_pwm.ChangeDutyCycle(0)
            
    except Exception as e:
        print(f"선풍기 제어 에러: {str(e)}")

def control_humidifier(power):
    """가습기(DC 모터) 제어 함수
    power: 1이면 켜짐, 0이면 꺼짐
    """
    try:
        print(f"가습기 제어: power = {power}")
        if power == 1:
            # 가습기 켜기
            GPIO.output(HUMIDIFIER, GPIO.HIGH)  # HIGH로 변경
            print("가습기 켜짐")
        else:
            # 가습기 끄기
            GPIO.output(HUMIDIFIER, GPIO.LOW)   # LOW로 변경
            print("가습기 꺼짐")
            
    except Exception as e:
        print(f"가습기 제어 에러: {str(e)}")

def cleanup():
    """프로그램 종료 시 GPIO 정리"""
    fan_pwm.stop()
    led_white_pwm.stop()
    led_yellow_pwm.stop()
    GPIO.cleanup()

def auto_led_control():
    """초음파 센서 기반 자동 LED 제어"""
    try:
        while True:
            distance = measure_distance()
            if distance is not None and distance <= 5:  # 5cm 이내 물체 감지
                controlLED("white", 0)      # 흰색 LED 끄기
                controlLED("yellow", 100)   # 노란색 LED 100%
            time.sleep(0.1)  # 0.1초 간격으로 측정
    except Exception as e:
        print(f"자동 LED 제어 에러: {str(e)}")

# 자동 LED 제어 스레드 시작
led_control_thread = threading.Thread(target=auto_led_control)
led_control_thread.daemon = True
led_control_thread.start()


# 센서 및 하드웨어 제어 코드
import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio

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

# 스위치 설정
SWITCH = 21
GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 초음파 센서 설정
TRIG = 20
ECHO = 16
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 서보모터 설정
SERVO = 18
GPIO.setup(SERVO, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO, 50)  # 50Hz PWM
servo_pwm.start(0)

# LED PWM 객체 전역 설정
led_white_pwm = GPIO.PWM(LED_WHITE, 100)
led_yellow_pwm = GPIO.PWM(LED_YELLOW, 100)
led_white_pwm.start(0)
led_yellow_pwm.start(0)

def read_adc(channel):
    """MCP3202에서 아날로그 값을 읽어오는 함수"""
    if channel != 0:
        raise ValueError('Channel must be 0')
    
    r = spi.xfer2([1, (2+channel)<<6, 0])
    adc_out = ((r[1]&15) << 8) + r[2]
    return adc_out

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
    """센서로부터 습도 값 수신 함수"""
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
    GPIO.output(TRIG, False)
    time.sleep(0.2)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

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

def control_servo(angle):
    """서모터 각도 제어 (0-180도)"""
    duty = (angle / 18.0) + 2.5
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)  # 서보 떨림 방지

def cleanup():
    """프로그램 종료 시 GPIO 정리"""
    servo_pwm.stop()
    led_white_pwm.stop()
    led_yellow_pwm.stop()
    GPIO.cleanup()
    spi.close()


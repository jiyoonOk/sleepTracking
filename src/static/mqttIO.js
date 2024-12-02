// 실시간 MQTT 데이터 처리 스크립트
let client = null; // MQTT 클라이언트의 역할을 하는 Client 객체를 가리키는 전역변수
let connectionFlag = false; // 연결 상태이면 true
const CLIENT_ID = "client-"+Math.floor((1+Math.random())*0x10000000000).toString(16) // 사용자 ID 랜덤 생성

function connect() {
    console.log("연결 시도...");
    if(connectionFlag == true) {
        console.log("이미 연결됨");
        return;
    }
    
    try {
        let broker = document.getElementById("broker").value;
        let port = 9001;
        
        console.log(`브로커 연결 시도: ${broker}:${port}`);
        
        client = new Paho.MQTT.Client(broker, Number(port), CLIENT_ID);
        client.onConnectionLost = onConnectionLost;
        client.onMessageArrived = onMessageArrived;
        
        client.connect({
            onSuccess: onConnect,
            onFailure: function(e) {
                console.error("연결 실패:", e);
                connectionFlag = false;
                client.disconnect();
            },
            useSSL: false,
            timeout: 5,
            keepAliveInterval: 60
        });
    } catch(e) {
        console.error("연결 시도 중 오류:", e);
        connectionFlag = false;
        client = null;
    }
}

// 브로커로의 접속이 성공할 때 호출되는 함수
function onConnect() {
	console.log("MQTT 연결 성공!");
	document.getElementById("messages").innerHTML += '<span>connected</span><br/>';
	connectionFlag = true;
	console.log("연결 상태 업데이트:", connectionFlag);
	
	// 센서 데이터 토픽 구독
	client.subscribe("temperature");
	client.subscribe("humidity");
	client.subscribe("light");
	client.subscribe("ultrasonic");
	
	// 초기 상태값 요청
	publish("request/temperature", "get");
	publish("request/humidity", "get");
	publish("request/light", "get");
}

function subscribe(topic) {
	if(connectionFlag != true) { // 연결되지 않은 경우
		alert("연결되지 않았음");
		return false;
	}

	// 구독 신청하였음을 <div> 영역에 출력
	document.getElementById("messages").innerHTML += '<span>구독신청: 토픽 ' + topic + '</span><br/>';
	client.subscribe(topic); // 브로커에 구독 신청
	return true;
}

function publish(topic, msg) {
    if(!client || !connectionFlag) {
        console.error('MQTT 클라이언트가 준비되지 않았습니다.');
        return false;
    }
    
    try {
        console.log(`메시지 전송: topic=${topic}, msg=${msg}`);
        let message = new Paho.MQTT.Message(msg.toString());  // 문자열로 변환
        message.destinationName = topic;
        client.send(message);  // publish 대신 send 사용
        return true;
    } catch(e) {
        console.error('메시지 전송 실패:', e);
        return false;
    }
}

function unsubscribe(topic) {
	if(connectionFlag != true) return; // 연결되지 않은 경우
	// 구독 신청 취소를 <div> 영역에 출력
	document.getElementById("messages").innerHTML += '<span>구독신청취소: 토픽 ' + topic + '</span><br/>';
	client.unsubscribe(topic, null); // 브로커에 구독 신청 취소
}

// 접속이 끊어졌을 때 호출되는 함수
function onConnectionLost(responseObject) { // responseObject는 응답 패킷
	document.getElementById("messages").innerHTML += '<span>오류 : 접속 끊어짐</span><br/>';
	if (responseObject.errorCode !== 0) {
		document.getElementById("messages").innerHTML += '<span>오류 : ' + responseObject.errorMessage + '</span><br/>';
	}
	connectionFlag = false; // 연결 되지 않은 상태로 설정
}

// 메시지가 도착할 때 호출되는 함수
function onMessageArrived(msg) {
    try {
        const value = parseFloat(msg.payloadString);
        if (isNaN(value)) {
            console.error("유효하지 않은 값:", msg.payloadString);
            return;
        }
        
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ${msg.destinationName}: ${value}`);
        
        switch(msg.destinationName) {
            case "temperature":
                document.getElementById("temperature").textContent = value.toFixed(1) + "°C";
                break;
            case "humidity":
                document.getElementById("humidity").textContent = value.toFixed(1) + "%";
                break;
            case "light":
                document.getElementById("light").textContent = value.toFixed(1) + "%";
                break;
            case "ultrasonic":
                addChartData(value);
                break;
        }
    } catch (e) {
        console.error("메시지 처리 중 에러:", e);
    }
}
// disconnection 버튼이 선택되었을 때 호출되는 함수
function disconnect() {
	if(connectionFlag == false) 
		return; // 연결 되지 않은 상태이면 그냥 리턴

	// 켜진 led 끄기
	if(document.getElementById("ledOn").checked == true) {
		client.send('led', "0", 0, false); // led를 끄도록 메시지 전송
		document.getElementById("ledOff").checked = true;	
	}
	client.disconnect(); // 브로커와 접속 해제
	document.getElementById("messages").innerHTML += '<span>연결종료</span><br/>';
	connectionFlag = false; // 연결 되지 않은 상태로 설정
}


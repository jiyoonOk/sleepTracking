// 실시간 차트 그래프 시각화 스크립트
let ctx = null;
let chart = null;
let config = {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: '온도 (°C)',
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                data: [],
                fill: false,
                yAxisID: 'y-temperature',
            },
            {
                label: '습도 (%)',
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                data: [],
                fill: false,
                yAxisID: 'y-humidity',
            },
            {
                label: '조도 (%)',
                borderColor: 'rgb(255, 206, 86)',
                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                data: [],
                fill: false,
                yAxisID: 'y-light',
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: '시간'
                }
            }],
            yAxes: [
                {
                    id: 'y-temperature',
                    position: 'left',
                    ticks: {
                        min: 0,
                        max: 40,
                        fontColor: 'rgb(255, 99, 132)'
                    },
                    scaleLabel: {
                        display: true,
                        labelString: '온도 (°C)',
                        fontColor: 'rgb(255, 99, 132)'
                    }
                },
                {
                    id: 'y-humidity',
                    position: 'right',
                    ticks: {
                        min: 0,
                        max: 100,
                        fontColor: 'rgb(54, 162, 235)'
                    },
                    scaleLabel: {
                        display: true,
                        labelString: '습도 (%)',
                        fontColor: 'rgb(54, 162, 235)'
                    }
                },
                {
                    id: 'y-light',
                    position: 'right',
                    ticks: {
                        min: 0,
                        max: 100,
                        fontColor: 'rgb(255, 206, 86)'
                    },
                    scaleLabel: {
                        display: true,
                        labelString: '조도 (%)',
                        fontColor: 'rgb(255, 206, 86)'
                    },
                    gridLines: {
                        drawOnChartArea: false
                    }
                }
            ]
        }
    }
};

let LABEL_SIZE = 20;
let tick = 0;

function drawSleepChart() {
    ctx = document.getElementById('sleepChart').getContext('2d');
    chart = new Chart(ctx, config);
    initSleepChart();
}

function initSleepChart() {
    const now = new Date();
    for(let i=0; i<LABEL_SIZE; i++) {
        chart.data.labels[i] = formatTime(new Date(now - (LABEL_SIZE - i) * 1000));
    }
    chart.update();
}

function formatTime(date) {
    return date.toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
}

function updateSleepChart(temperature, humidity, light) {
    if (!chart || !chart.data || !chart.data.datasets) {
        console.error("차트가 초기화되지 않음");
        return;
    }

    const now = new Date();
    const timeStr = formatTime(now);

    try {
        chart.data.datasets.forEach((dataset, index) => {
            const value = index === 0 ? temperature : 
                         index === 1 ? humidity : light;
            
            if (dataset.data.length >= LABEL_SIZE) {
                dataset.data.shift();
                chart.data.labels.shift();
            }
            dataset.data.push(value);
        });

        chart.data.labels.push(timeStr);
        chart.update();
    } catch (e) {
        console.error("차트 데이터 추가 중 에러:", e);
    }
}
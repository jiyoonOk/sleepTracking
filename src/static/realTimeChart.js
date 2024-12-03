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
                        max: 50,
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

function drawChart() {
    ctx = document.getElementById('sleepChart').getContext('2d');
    chart = new Chart(ctx, config);
    init();
}

function init() {
    const now = new Date();
    for(let i=0; i<LABEL_SIZE; i++) {
        chart.data.labels[i] = new Date(now - (LABEL_SIZE - i) * 1000).toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    chart.update();
}

function addChartData(datasetIndex, value) {
    if (!chart || !chart.data || !chart.data.datasets) {
        console.error("차트가 초기화되지 않음");
        return;
    }
    
    try {
        const dataset = chart.data.datasets[datasetIndex];
        const n = dataset.data.length;
        
        if(n < LABEL_SIZE) {
            dataset.data.push(value);
        } else {
            dataset.data.push(value);
            dataset.data.shift();
            
            // 모든 데이터셋이 같은 레이블을 공유하므로 한 번만 업데이트
            if(datasetIndex === 0) {
                chart.data.labels.push(new Date().toLocaleTimeString('ko-KR', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }));
                chart.data.labels.shift();
            }
        }
        
        chart.update();
    } catch (e) {
        console.error("차트 데이터 추가 중 에러:", e);
    }
}
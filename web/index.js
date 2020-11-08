let pointApplied = false;
let highChart;

const chartColours = ['darkgreen', 'green', 'darkblue'];

const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 1000
})

function setLangLat(latLng) {    
    document.getElementById("latCoord").innerHTML = latLng.lat;
    document.getElementById("langCoord").innerHTML = latLng.lng;
}

function clearLangLat() {    
    document.getElementById("latCoord").innerHTML = "None";
    document.getElementById("langCoord").innerHTML = "None";

    clearMarker();
    pointApplied = false;
    handlePointApplied();
    
    document.getElementById("apply").disabled = true;

    highChart.destroy();
}

function applyLangLat(){    
    const lat = document.getElementById("latCoord").innerHTML;
    const lng = document.getElementById("langCoord").innerHTML;

    if (isNaN(lat) ||isNaN(lng)){
        return;
    }

    axiosInstance({
        method: 'post',
        url: '/api',
        data: {
            'lat': lat,
            'lng': lng
        }
    }).then(function (response) {
        const data = response.data;
        const bbox = data.bbox;

        addBoundingBox(bbox);
        pointApplied = true;
        handlePointApplied();

        initChart();
    })
}

function handlePointApplied() {
    if (pointApplied){
        document.getElementById("apply").style.display = "none";
        document.getElementById("clear").style.display = "inline-block";
    } else {
        document.getElementById("apply").style.display = "inline-block";
        document.getElementById("clear").style.display = "none";
    }
}

function isPointApplied() {
    return pointApplied;
}

function handleLayerChange(selectedValue) {
    // Remove existing chart
    highChart.destroy();

    // TODO Determine what chart we want now.

    // Make new chart
}

function initChart() {
    
    highChart = Highcharts.chart('chartContainer', {
        title: {
            text: 'Top shit graph.'
        },
    
        yAxis: {
            title: {
                text: 'Some cool metric'
            }
        },
    
        xAxis: {
            type: 'datetime',
            tickInterval: 3 * 30 * 24 * 3600 * 1000
        },
    
        legend: {
            enabled: false
        },

        plotOptions: {
            series: {
                color: 'darkgreen',
                type: 'spline',
                pointStart: Date.UTC(2018, 01, 01)
            }
        },
    
        series: [{
            name: '',
            data: [[Date.UTC(2018, 01, 01), 43934], [Date.UTC(2018, 04, 01), 52503], [Date.UTC(2018, 07, 01), 57177], [Date.UTC(2018, 10, 01), 69658], [Date.UTC(2019, 01, 01), 97031], [Date.UTC(2019, 04, 01), 119931], [Date.UTC(2019, 07, 01), 137133], [Date.UTC(2019, 10, 01), 123123]]
        }]
    });
    
}
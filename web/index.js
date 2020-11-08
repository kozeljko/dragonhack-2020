let pointApplied = false;
let highChart;

const chartCombos = {
    default: {
        name: "Weather data",
        tickInterval: 3 * 30 * 24 * 3600 * 1000
    }
}

const weatherSeries = [{
    key: 'maxtempC',
    name: 'Max temperature',
    unit: '°C',
    color: 'darkgreen'
},{
    key: 'mintempC',
    name: 'Min temperature',
    unit: '°C',
    color: 'green'
},{
    key: 'totalSnow_cm',
    name: 'Max temperature',
    unit: 'cm2',
    color: 'darkblue'
},{
    key: 'precipMM',
    name: 'The fuck',
    unit: '°C',
    color: 'blue'
}];

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
        },
        timeout: 10000
    }).then(function (response) {
        const data = response.data;
        console.log(data);
        
        const bbox = data.bbox;
        addBoundingBox(bbox);

        prepareSeries(data);
        determineChart();

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

function prepareSeries(payload) {
    // Weather
    const weatherData = payload['weather'];
    weatherSeries.forEach(function(config) {
        const timeSeries = weatherData[config.key]
        config.series = timeSeries.map(o => [Date.parse(o['time']), parseFloat(o['value'])])
    })

    // TODO Vegetation
}

function determineChart() {
    const currentLayer = getLayerId();

    initChart(chartCombos.default, weatherSeries)
}

function initChart(chart, seriesArray) {
    const preparedSeries = seriesArray.map(o => {
        let output = {}
        output.name = o.name;
        output.data = o.series;
    })

    console.log(preparedSeries);
    
    
    highChart = Highcharts.chart('chartContainer', {
        title: {
            text: chart.name
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
                type: 'spline'
            }
        },
    
        series: preparedSeries
    });
    
}
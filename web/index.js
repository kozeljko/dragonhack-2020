let pointApplied = false;
let highChart;

const chartCombos = {
    default: {
        name: "Weather data",
        tickInterval: 3 * 30 * 24 * 3600 * 1000,
        yAxis: [{
            id: "temp",
            labels: {
                format: '{value}°C'
            },
            title: {
                text: 'Temperature'
            },
            opposite: true
        }, {
            id: "pad",
            labels: {
                format: '{value}cm2'
            },
            title: {
                text: 'Fall units'
            }
        }]
    }, 
    one: {
        name: "Vegetation trend",
        tickInterval: 3 * 30 * 24 * 3600 * 1000,
        yAxis: [{
            id: "veg",
            labels: {
                format: '{value}%'
            },
            title: {
                text: 'Vegetation index'
            }
        }]
    }
}

const weatherSeries = [{
    key: 'maxtempC',
    name: 'Max temperature',
    unit: '°C',
    color: 'darkgreen',
    yAxis: 'temp'
},{
    key: 'mintempC',
    name: 'Min temperature',
    unit: '°C',
    color: 'green',
    yAxis: 'temp'
},{
    key: 'totalSnow_cm',
    name: 'Snow',
    unit: 'cm2',
    color: 'darkblue',
    yAxis: 'pad'
},{
    key: 'precipMM',
    name: 'Precipitation',
    unit: 'cm2',
    color: 'blue',
    yAxis: 'pad'
}];

const vegSeries = [{
    key: 'veg',
    name: 'Vegetation index',
    unit: '%',
    color: 'darkgreen',
    yAxis: 'veg'
}]

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
        timeout: 100000
    }).then(function (response) {
        const data = response.data;
        console.log(data);
        
        const bbox = data.bbox;
        addBoundingBox(bbox);

        prepareSeries(data);
        determineChart();

        pointApplied = true;
        handlePointApplied();
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

function handleLayerChange() {
    if (pointApplied) {
            determineChart();
    }
}

function prepareSeries(payload) {
    // Weather
    const weatherData = payload['weather'];
    weatherSeries.forEach(function(config) {
        const timeSeries = weatherData[config.key]
        config.series = timeSeries.map(o => [Date.parse(o['time']), parseFloat(o['value'])])
    })

    // Vegetation
    const vegData = payload['vegetation'];
    vegSeries.forEach(function(config){
        // TODO
    })
}

function determineChart() {
    const currentLayer = getLayerId();
    console.log(currentLayer);
    

    if (currentLayer === 'default') {
        initChart(chartCombos.default, weatherSeries);
    } else {
        initChart(chartCombos.one, vegSeries);
    }
}

function initChart(chart, seriesArray) {
    console.log(seriesArray);
    const preparedSeries = seriesArray.map(o => {
        let output = {}
        output.name = o.name;
        output.data = o.series;
        output.yAxis = o.yAxis;
        output.tooltip = {
            valueSuffix: o.unit
        }
        return output;
    });
    
    
    highChart = Highcharts.chart('chartContainer', {
        title: {
            text: chart.name
        },
    
        yAxis: chart.yAxis,
    
        xAxis: {
            type: 'datetime',
            tickInterval: 3 * 30 * 24 * 3600 * 1000
        },
    
        legend: {
            enabled: false
        },

        colors: ['darkgreen', 'green', 'darkblue', 'blue'],

        plotOptions: {
            series: {
                type: 'spline'
            }
        },
    
        series: preparedSeries
    });
    
}
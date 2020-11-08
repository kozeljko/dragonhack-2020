let pointApplied = false;
let highChart;

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

function initChart() {
    
    highChart = Highcharts.chart('chartContainer', {
        title: {
            text: 'Solar Employment Growth by Sector, 2010-2016'
        },
    
        subtitle: {
            text: 'Source: thesolarfoundation.com'
        },
    
        yAxis: {
            title: {
                text: 'Number of Employees'
            }
        },
    
        xAxis: {
            accessibility: {
                rangeDescription: 'Range: 2010 to 2017'
            }
        },
    
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                },
                pointStart: 2010
            }
        },
    
        series: [{
            name: 'Installation',
            data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
        }, {
            name: 'Manufacturing',
            data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
        }, {
            name: 'Sales & Distribution',
            data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
        }, {
            name: 'Project Development',
            data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
        }, {
            name: 'Other',
            data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
        }]
    });
    
}
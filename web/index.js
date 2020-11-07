const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 1000
})

function setLangLat(latLng) {    
    document.getElementById("latCoord").innerHTML = latLng.lat;
    document.getElementById("langCoord").innerHTML = latLng.lng;
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
    })
}
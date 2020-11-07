function setLangLat(latLng) {    
    document.getElementById("latCoord").innerHTML = latLng.lat;
    document.getElementById("langCoord").innerHTML = latLng.lng;
}

function applyLangLat(){    
    const lat = document.getElementById("latCoord").innerHTML;
    const lng = document.getElementById("langCoord").innerHTML;

    console.log("Found: " + lat + " " + lng);
}
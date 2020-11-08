let marker;
let rectangle;
let map;
let currentLayer;
let layerMap = {};


document.addEventListener("DOMContentLoaded", function () {
    buildLayerMap();

    currentLayer = layerMap.default;
    map = L.map("sentinelMap", {
        center: [8.463033827391877, 4.56756591796875], // lat/lng in EPSG:4326
        zoom: 12,
        layers: [currentLayer]
    });

    // Function for handling user click.
    map.on('click', function (e) {
        if (isPointApplied()) {
            return;
        }

        document.getElementById("apply").disabled = false;
        addMarker(e.latlng);
    });
});

function addMarker(latLng) {
    if (marker === undefined) {
        marker = L.marker(latLng).addTo(map);
    } else {
        marker.setLatLng(latLng);
    }

    setLangLat(latLng);
}

// Bounds are: [[NORTH, WEST], [SOUTH, EAST]]
function addBoundingBox(bbox) {
    if (rectangle === undefined) {
        rectangle = L.rectangle(bbox, {color: 'blue', weight: 1}).addTo(map);
    } else {
        rectangle.setBounds(bbox);
    }
}

function clearMarker() {
    if (marker != undefined) {
        map.removeLayer(marker);
        marker = undefined;
    }

    if (rectangle != undefined) {
        map.removeLayer(rectangle);
        rectangle = undefined;
    }
}

function layerChange() {
    const selectedValue = document.getElementById("selectLayer").value;
    const selectedLayer = layerMap[selectedValue];

    map.removeLayer(currentLayer);
    selectedLayer.addTo(map);
}

// This functions needs to be filled out in order to set up all layers.
function buildLayerMap(){
    // OpenStreetMap
    let osm = L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    });

    // Sentinel Hub WMS service
    // tiles generated using EPSG:3857 projection - Leaflet takes care of that
    let baseUrl =
        "https://services.sentinel-hub.com/ogc/wms/ca37eeb6-0a1f-4d1b-8751-4f382f63a325";
    let sentinelHub = L.tileLayer.wms(baseUrl, {
        tileSize: 512,
        attribution:
            '&copy; <a href="http://www.sentinel-hub.com/" target="_blank">Sentinel Hub</a>',
        urlProcessingApi:
            "https://services.sentinel-hub.com/ogc/wms/aeafc74a-c894-440b-a85b-964c7b26e471",
        maxcc: 0,
        minZoom: 6,
        maxZoom: 16,
        preset: "CUSTOM",
        evalscript: "cmV0dXJuIFtCMDEqMi41LEIwMSoyLjUsQjA0KjIuNV0=",
        evalsource: "S2",
        PREVIEW: 3,
        layers: "NDVI",
        time: "2020-05-01/2020-11-07"
    });
    let agriHub = L.tileLayer.wms(baseUrl, {
        tileSize: 512,
        attribution: '&copy; <a href="http://www.sentinel-hub.com/" target="_blank">Sentinel Hub</a>',
                           urlProcessingApi:"https://services.sentinel-hub.com/ogc/wms/aeafc74a-c894-440b-a85b-964c7b26e471", 
                        maxcc:20, 
                        minZoom:6, 
                        maxZoom:16, 
                        preset:"AGRICULTURE", 
                        layers:"AGRICULTURE", 
                        time:"2020-05-01/2020-11-07", 
    
    });

    layerMap.default = osm;
    layerMap.one = sentinelHub;
    layerMap.two = agriHub;
}
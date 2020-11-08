let marker;
let rectangle;
let map;
let currentLayerId;
let currentLayer;
let layerMap = {};


document.addEventListener("DOMContentLoaded", function () {
    buildLayerMap();

    currentLayerId = 'default';
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

    map.panTo([46.24189856712798, 14.355354309082033])
});

function addMarker(latLng) {
    if (marker === undefined) {
        let greenIcon = new L.Icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        marker = L.marker(latLng, {icon: greenIcon}).addTo(map);
    } else {
        marker.setLatLng(latLng);
    }

    setLangLat(latLng);
}

// Bounds are: [[NORTH, WEST], [SOUTH, EAST]]
function addBoundingBox(bbox) {
    if (rectangle === undefined) {
        rectangle = L.rectangle(bbox, {color: 'darkgreen', weight: 1}).addTo(map);
    } else {
        rectangle.setBounds(bbox);
    }
}

function clearMarker() {
    if (marker !== undefined) {
        map.removeLayer(marker);
        marker = undefined;
    }

    if (rectangle !== undefined) {
        map.removeLayer(rectangle);
        rectangle = undefined;
    }
}

function layerChange() {
    const selectedValue = document.getElementById("selectLayer").value;
    const selectedLayer = layerMap[selectedValue];

    map.removeLayer(currentLayer);
    selectedLayer.addTo(map);
    currentLayerId = selectedValue;
    currentLayer = selectedLayer;

    handleLayerChange(selectedValue);
}

function getLayerId() {
    return currentLayerId;
}

// This functions needs to be filled out in order to set up all layers.
function buildLayerMap() {
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
        attribution: '&copy; <a href="http://www.sentinel-hub.com/" target="_blank">Sentinel Hub</a>',
        urlProcessingApi: "https://services.sentinel-hub.com/ogc/wms/aeafc74a-c894-440b-a85b-964c7b26e471",
        maxcc: 20,
        minZoom: 6,
        maxZoom: 16,
        preset: "DRAGONHACK",
        layers: "DRAGONHACK",
        time: "2020-05-01/2020-11-08",

    });

    layerMap.default = osm;
    layerMap.one = sentinelHub;
}
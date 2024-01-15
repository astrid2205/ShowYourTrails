var map, newLocation;
var polylines = {}
var bounds = [[180, 180],[-180, -180]]
var currentTrails = []

// Get Json data from the database and display trail maps in the web application
document.addEventListener('DOMContentLoaded', () => {
    renderMap();
    changeMapCenter();
    drawTrails();

    // Draw new trails when the map is scrolled / zoomed
    map.on('moveend', () => {
        updateBounds();
        drawTrails();
    });
})


// Draw the map using user location as center. If location is not available, draw Taiwan.
function renderMap() {
    coords = JSON.parse(document.getElementById('coords').textContent);
    if (coords == "") {
        setMap([23.5310, 121.0071], 6);
    } else {
        setMap(coords, 10);
    }
    updateBounds();
}


// Change the map center and update bounds according to user search input.
function changeMapCenter() {
    searchbtn = document.getElementById('search-btn');
    searchbox = document.getElementById('search-box');

    // When user click the search button
    searchbtn.addEventListener("click", () => {
        moveMap();
    })
    
    // When user hit enter in search box
    searchbox.addEventListener("keyup", (e) => {
        if (e.key === "Enter") {
            moveMap();
        }
    })

    // Move the map according to current bounds
    function moveMap() {
        text = searchbox.value;
        // console.log(text);
        if (text !== '') {
            fetch(`https://nominatim.openstreetmap.org/search?q=${text}&format=json`)
            .then(response => response.json())
            .then(result => {
                // console.log(result);
                if (result.length !== 0) {
                    boundingbox = result[0].boundingbox;
                    bounds = [[boundingbox[0], boundingbox[2]], [boundingbox[1], boundingbox[3]]];
                    map.fitBounds(bounds);
                    zoom = map.getZoom();
                    if (zoom < 4) {
                        map.setView([result[0].lat, result[0].lon], 4);
                    }
                }
            });
        }
    }
}


// Update the map bounds after the map is scrolled / zoomed
function updateBounds() {
    bounds[0][0] = (map.getBounds().getSouthWest().lat);
    bounds[0][1] = (map.getBounds().getSouthWest().lng);
    bounds[1][0] = (map.getBounds().getNorthEast().lat);
    bounds[1][1] = (map.getBounds().getNorthEast().lng);    
}


// Draw (maximum) 10 trails in current bounds
function drawTrails() {
    lat_min = Math.min(bounds[0][0], bounds[1][0]);
    lat_max = Math.max(bounds[0][0], bounds[1][0]);
    lon_min = Math.min(bounds[0][1], bounds[1][1]);
    lon_max = Math.max(bounds[0][1], bounds[1][1]);

    fetch(`/api/explore_maps/?lat_min=${lat_min}&lat_max=${lat_max}&lon_min=${lon_min}&lon_max=${lon_max}`)
    .then(response => response.json())
    .then(result => {
        // console.log(result);
        currentTrails = []
        if (result.length !== 0) {
            for (const trail of result) {
                drawTrail(trail);
                generateLink(trail);
                currentTrails.push(trail.trail.id);
            }
        } else {
            console.log("No trail found.");
        }
        clearTrail();
    })
    .catch(error => {
        console.error(`Failed to fetch: ${error}`);
    });
}


// Remove the previous trails that is not in current map bounds from the map
function clearTrail() {
    for (const [key, value] of Object.entries(polylines)) {
        if (!currentTrails.includes(Number(key))) {
            value.removeFrom(map);
            trail_link = document.getElementById(key);
            if (trail_link !== null) {
                trail_link.remove();
            }
        }
    }
}


// Draw single trail on the map
function drawTrail(trail) {
    if (trail.trail.id in polylines) {
        polylines[trail.trail.id].addTo(map);
    } else {
        line = L.polyline(trail.coordinates, { color: randomRGB() });
        trail_detail = `<div><b><a href="/trail/${trail.trail.id}">${trail.trail.trail_name}</a></b></div><br>
                                        <div>Distance: ${trail.trail.distance} km</div>
                                        <div>Ascent: ${Number(trail.trail.sum_uphill).toFixed(0)} m</div>
                                        <div>Duration: ${trail.trail.duration}</div>`;
        line.bindPopup(trail_detail);
        polylines[trail.trail.id] = line;
        line.addTo(map);
    }
}


// Generate trail title with link to put on the trails list
function generateLink(trail) {
    if (document.getElementById(trail.trail.id) === null) {
        c = document.getElementById('trails-explore-container');
        trail_link = `<a href="/trail/${trail.trail.id}">${trail.trail.trail_name}</a>`
        const div = document.createElement("div");
        div.innerHTML = trail_link;
        div.id = trail.trail.id;
        div.className = 'trails-explore-link';
        c.appendChild(div);
    }
}


// Draw the map in HTML (using Leaflet library)
function setMap(map_center, zoom) {
    map = L.map('trailmap').setView(map_center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}


function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
  

function randomRGB() {
    return `rgb(255, ${random(0, 187)}, 0)`;
}
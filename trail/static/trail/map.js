var map, marker, coordinates, dist_elev, map_center;

// Get Json data from the database and display trail map and elevation profile in the web application
document.addEventListener('DOMContentLoaded', () => {
    const trailID = Number(document.getElementById("trail_id").textContent)

    fetch(`/api/trailmaps/?trail=${trailID}`)
    .then(response => response.json())
    .then(result => {
        trailmap = result["results"][0]
        coordinates = trailmap.coordinates;
        dist_elev = trailmap.dist_elev;
        map_center = trailmap.map_center;
        setMap();
        setElevation();
    })
    .catch(error => {
        console.error(`Failed to fetch: ${error}`);
    });
})

// Draw the map in HTML (using Leaflet library)
function setMap() {
    map = L.map('trailmap').setView(map_center, 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    var polyline = L.polyline(coordinates, { color: 'red' }).addTo(map);
    map.fitBounds(polyline.getBounds());
}

// Draw the elevation profile in HTML (Using Chart.js library)
function setElevation() {
    const ctx = document.getElementById('elevation-profile');
    const trailData = dist_elev[1]
    let trailLabel = dist_elev[0].map((value) => value/1000)
    marker = L.circleMarker(coordinates[0], {radius: 7, fillColor:'#3388ff', fillOpacity: 0, opacity: 0})
    marker.addTo(map)
    let pointIndex;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trailLabel,
            datasets: [{
                label: 'Elevation',
                data: trailData,
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension:0.3
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    max: `${(trailLabel[trailLabel.length - 1]).toFixed(2)}`,
                    ticks: {
                        callback: value => `${value} km`
                    }
                },
                y: {
                    min: Math.min(Math.min(trailData) - 100, 0), 
                    type: 'linear',
                    ticks: {
                        callback: value => `${value} m`
                    },
                },
            },
            interaction: { intersect: false, mode: 'index'},
            tooltip: { position: 'nearest' },
            plugins: {
                legend: { display: false },
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        // Format the tooltip
                        title: (tooltipItems) => {
                            return "Distance: " + tooltipItems[0].label + ' km'
                        },
                        // Move the marker on the map according to the position on the elevation profile and show elevation on the tooltip
                        label: (context) => {
                            pointIndex = context.dataIndex 
                            marker.setLatLng(L.latLng(coordinates[pointIndex]))
                            return "Elevation: " + context.raw + ' m'
                        }
                    }
                },
            },
        },
    });
    // Hide the marker on the map when the mouse is not on the elevation profile
    ctx.onmouseout = () => {marker.setStyle({opacity:0, fillOpacity:0})}
    ctx.onmouseover = () => {marker.setStyle({opacity:1, fillOpacity:0.8})}
}


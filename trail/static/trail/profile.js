var map, userId;
var polylines = {}
var bounds = [[180, 180],[-180, -180]]

// Get Json data from the database and display trail maps in the web application
document.addEventListener('DOMContentLoaded', () => {
    drawTrails();
    ctrlDisplayTrail();
    followUser();
})

// Draw all the trails the profile owner set to public
function drawTrails() {
    userId = Number(document.getElementById('trail_user_id').textContent);

    fetch(`/api/user_maps/${userId}/`)
    .then(response => response.json())
    .then(result => {
        if (result.length !== 0) {
            setMap(result[0].map_center);

            for (const trail of result) {
                drawTrail(trail);
            }
            map.fitBounds(bounds);
        } else {
            console.log("No trail found.");
            document.querySelector('#profile-trail-table').remove();
            setMap([23.5310, 121.0071]);
        }
    })
    .catch(error => {
        console.error(`Failed to fetch: ${error}`);
    });
}

// Draw single trail on the map
function drawTrail(trail) {
    line = L.polyline(trail.coordinates, { color: randomRGB() });
    trail_detail = `<div><b><a href="/trail/${trail.trail.id}">${trail.trail.trail_name}</a></b></div><br>
                                    <div>Distance: ${trail.trail.distance} km</div>
                                    <div>Ascent: ${Number(trail.trail.sum_uphill).toFixed(0)} m</div>
                                    <div>Duration: ${trail.trail.duration}</div>`;
    line.bindPopup(trail_detail);
    polylines[trail.trail.id] = line;
    getLineBounds(line);
    line.addTo(map);
}

// Display the trail on the map when the checkbox is clicked, and update the database
// This function is only available for for profile owner
function ctrlDisplayTrail() {
    const i = document.querySelectorAll('input')
    i.forEach(item => {
        item.onclick = (e) => {
            console.log(e.target.id, e.target.checked)
            trail = e.target 

            // Change display on map
            if (trail.checked) {
                if (trail in polylines) {
                    polylines[trail.id].addTo(map);
                } else {
                    fetch(`/api/trailmaps/?trail=${trail.id}`)
                    .then(response => response.json())
                    .then(result => {
                        trailmap = result["results"][0];
                        drawTrail(trailmap);
                    })
                    .catch(error => {
                        console.error(`Failed to fetch: ${error}`);
                    });
                }
            } else {
                polylines[trail.id].removeFrom(map);
            }

            // Update trail public status
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch(`/api/trails/${trail.id}/`, {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': csrftoken,
                    "Content-type": "application/json; charset=UTF-8",
                },
                mode: 'same-origin',
                body: JSON.stringify({"public": trail.checked})
            })
            .catch(error => {
                console.log('Error:', error);
            });
        }
    })
}

// Draw the map in HTML (using Leaflet library)
function setMap(map_center) {
    map = L.map('trailmap').setView(map_center, 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}

// Update the bounds if the input line exceeds the current bounds
function getLineBounds(line) {
    bounds[0][0] = Math.min((line.getBounds().getSouthWest().lat), bounds[0][0]);
    bounds[0][1] = Math.min((line.getBounds().getSouthWest().lng), bounds[0][1]);
    bounds[1][0] = Math.max((line.getBounds().getNorthEast().lat), bounds[1][0]);
    bounds[1][1] = Math.max((line.getBounds().getNorthEast().lng), bounds[1][1]);
}

function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
  
  function randomRGB() {
    return `rgb(255,${random(0, 187)},0)`;
}

function followUser() {
    const follow_user_button = document.getElementById('follow-user-button');
    const request_user_id = Number(document.getElementById('request_user_id').textContent);
    const trail_user_id = Number(document.getElementById('trail_user_id').textContent);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (follow_user_button !== null) {
        follow_user_button.onclick = () => {
            c = follow_user_button.textContent;
            console.log(c)
        
        if (c === 'Follow') {
            follow_user_button.innerHTML = '<span>Followed!</span>';
            save_method = 'POST';
            api_route = `/api/followeduser/`
        } else if (c === 'Followed!') {
            follow_user_button.textContent = 'Follow';
            save_method = 'DELETE';
            const user_followed_id = Number(document.getElementById('user_followed_id').textContent);
            api_route = `/api/followeduser/${user_followed_id}`
        }
        
        // Update usef following status
        fetch(api_route, {
            method: save_method,
            headers: {
                'X-CSRFToken': csrftoken,
                "Content-type": "application/json; charset=UTF-8",
            },
            mode: 'same-origin',
            body: JSON.stringify({
                "user": request_user_id,
                "following": trail_user_id,
            })
        })
        .catch(error => {
            console.log('Error:', error);
        });
        
        changeBtnStyle(follow_user_button)
        }
    }
}

function changeBtnStyle(button) {
    button.classList.toggle("btn-outline-primary");
    button.classList.toggle("btn-primary");
    button.classList.toggle("unfollow");
}
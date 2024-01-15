document.addEventListener('DOMContentLoaded', () => {
    saveTrail();
})


function saveTrail() {
    const save_trail_button = document.getElementById('save-trail-button');
    const request_user_id = Number(document.getElementById('request_user_id').textContent);
    const trail_id = Number(document.getElementById('trail_id').textContent);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (save_trail_button !== null) {
        save_trail_button.onclick = () => {
            c = save_trail_button.textContent;
            
            if (c === 'Save the trail') {
                save_trail_button.textContent = 'Saved!';
                save_method = 'POST';
                api_route = `/api/savedtrails/`
            } else {
                save_trail_button.textContent = 'Save the trail';
                save_method = 'DELETE';
                const trail_saved_id = Number(document.getElementById('trail_saved_id').textContent);
                api_route = `/api/savedtrails/${trail_saved_id}`
            }
    
            // Update trail saved status
            fetch(api_route, {
                method: save_method,
                headers: {
                    'X-CSRFToken': csrftoken,
                    "Content-type": "application/json; charset=UTF-8",
                },
                mode: 'same-origin',
                body: JSON.stringify({
                    "user": request_user_id,
                    "trail": trail_id,
                })
            })
            .catch(error => {
                console.log('Error:', error);
            });
    
            changeBtnStyle(save_trail_button)
        }
    }
    
}


function changeBtnStyle(button) {
    button.classList.toggle("btn-outline-primary");
    button.classList.toggle("btn-primary");
}
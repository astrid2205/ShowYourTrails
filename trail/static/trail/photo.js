document.addEventListener('DOMContentLoaded', () => {
    showFullSizePhoto();
    deletePhoto();
})


function showFullSizePhoto() {
    const b = document.querySelectorAll('.thumbnail-img')
    const photo = document.getElementById('full-size-photo')
    if (photo !== null) {
        b.forEach(item => {
            item.onclick = (e) => {
                fetch(`/api/photofiles/${e.target.id}`)
                .then(response => response.json())
                .then(data => {
                    photo.src=data.photo_file
                })
                .catch(error => {
                    console.log('Error:', error);
                });
            }
        })
    }
}

function deletePhoto() {
    const b = document.querySelectorAll('.edit-thumbnail-img')
    const deletePhotoBtn = document.getElementById('delete-photo-btn')
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var toBeDeleted = new Set()

    // Add the clicked photo to the toBeDeleted set
    b.forEach(item => {
        item.onclick = (e) => {
            photo = e.target;
            if (toBeDeleted.has(photo.id)) {
                photo.style.border = "";
                photo.style.color = "";
                toBeDeleted.delete(photo.id);
            } else {
                photo.style.border = "solid";
                photo.style.color = "red";
                toBeDeleted.add(photo.id);
            }
        }
    })
    
    // Delete the photo in the database
    if (deletePhotoBtn !== null) {
        deletePhotoBtn.onclick = () => {
            if (toBeDeleted.size !== 0) {
                toBeDeleted.forEach((photoID) => {
                    console.log(photoID)
                    fetch(`/api/photofiles/${photoID}`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            "Content-type": "application/json; charset=UTF-8",
                        },
                        mode: 'same-origin',
                    })
                    .catch(error => {
                        console.log('Error:', error);
                    });
                    document.getElementById(photoID).remove()
                })
            }
            toBeDeleted.clear()
        }
    }
}

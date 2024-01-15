document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("change_profile_photo").onchange = () => {
        document.getElementById("profile_photo_form").submit();
    };
})
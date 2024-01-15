document.addEventListener('DOMContentLoaded', () => {
    const d = document.querySelectorAll(".confirm-delete")
    d.forEach(b => {
        b.onclick = () => confirm("Are you sure? Deleting a trail cannot be undone.")
    })
})

let body = document.querySelector('body')
let meta = document.querySelector('meta[name="theme-color"]')

function updateColors() {
    let hour = new Date().getHours()

    if (hour >= 22 || hour <= 5) {
        body.classList.add('dark')
        meta.setAttribute('content', '#0c0c0c')
    } else {
        body.classList.remove('dark')
        meta.setAttribute('content', '#f4f4f4')
    }
}

updateColors()
setInterval(updateColors, 5000)
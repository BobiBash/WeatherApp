const body = document.body
const images = BACKGROUND_IMAGES

const image_count = images.length

let random_image = Math.floor(Math.random() * image_count)

window.onload = function (){
    body.style.background = `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(${images[random_image]}) center/cover no-repeat fixed`;
}
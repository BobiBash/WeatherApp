const ParentContainer = document.getElementById("hourly-wrapper")
const ForeCastDataElement = document.getElementById("hourly-forecast-data");
const ForeCastData = JSON.parse(ForeCastDataElement.textContent);

console.log(ForeCastData);

ForeCastData.forEach(hour => {
    const mainContainer = document.createElement("div")
    mainContainer.classList.add("weather-wrapper")

    const TitleContainer = document.createElement("div");
    TitleContainer.classList.add("title-content");

    const title = document.createElement("h2");
    title.textContent = hour.time;
    TitleContainer.appendChild(title);

    mainContainer.appendChild(TitleContainer);

    mainContainer.innerHTML += `
    <div class="weather-container">
        <div class="weather-info">
            <img class="weather-icon" src="/static/node_modules/@bybas/weather-icons/design/fill/animation-ready/${hour.icon}.svg">
            <p class="weather-temp">${hour.temperature}°</p>
            <p class="temp-degrees">C</p>
            <p class="weather-real-feel">RealFeel ${hour.apparent_temperature}°</p>
            <p class="weather-description">${hour.description}</p>
        </div>
        <div class="weather-details-container">
            <div class="weather-details">
                <span class="label">Wind</span>
                <span class="value">${hour.wind_speed}km/h</span>
            </div>
            <div class="weather-details">
                <span class="label">Wind Gusts</span>
                <span class="value">${hour.wind_gusts}km/h</span>
            </div>
            <div class="weather-details">
                <span class="label">Air Quality</span>
                <span class="value">${hour.air_quality}</span>
            </div>
        </div>
    </div>`


    ParentContainer.appendChild(mainContainer);

});
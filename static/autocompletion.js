const input = document.getElementById('cityInput');
const datalist = document.getElementById('citySuggestions');
const form = document.getElementById('searchbar')


input.value = '';

window.addEventListener('pageshow', (event) => {
    input.value = '';
});

input.addEventListener('input', async (e) => {
    const query = e.target.value;
    if (query.length < 2) return;

    const response = await fetch(`/autocomplete/?q=${query}`);
    const suggestions = await response.json();

    datalist.innerHTML = '';

    suggestions.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        datalist.appendChild(option);
    });
});

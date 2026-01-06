const input = document.getElementById('cityInput');
const suggestionsContainer = document.getElementById('citySuggestions');
const form = document.getElementById('searchbar');

input.value = '';

window.addEventListener('pageshow', (event) => {
    input.value = '';
});


input.addEventListener('input', async (e) => {
    const query = e.target.value;

    if (query.length < 2) {
        suggestionsContainer.innerHTML = '';
        return;
    }

    const response = await fetch(`/autocomplete/?q=${query}`);
    const suggestions = await response.json();
    console.log(suggestions)

    suggestionsContainer.innerHTML = '';

    suggestions.forEach(city => {
        const options = document.createElement('li');
        options.classList.add('suggestion');
        options.textContent = city;

        options.addEventListener('click', () => {
            input.value = city;
            suggestionsContainer.innerHTML = '';
            form.submit();
        });

        suggestionsContainer.appendChild(options);

    });
});



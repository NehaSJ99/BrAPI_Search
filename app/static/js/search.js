let currentSearchResults = [];
let currentSearchQuery = '';

function performSearch(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    if (!validateForm()) {
        return;
    }

    // Prepare data to send in the POST request
    const formData = new FormData();
    formData.append('query', document.getElementById('searchBox').value.trim());
    document.querySelectorAll('input[name="servers[]"]:checked').forEach(server => formData.append('servers[]', server.value));
    document.querySelectorAll('input[name="search_for"]:checked').forEach(item => formData.append('search_for', item.value));

    fetch('/search', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Store results in sessionStorage
        sessionStorage.setItem('searchResults', JSON.stringify(data));
        sessionStorage.setItem('searchQuery', formData.get('query'));
        sessionStorage.setItem('showResults', 'true'); // Flag to show results

        // Update the search term display and results
        displayResults(formData.get('query'), data);
    })
    .catch(error => {
        console.error('Error fetching search results:', error);
        document.getElementById('results-container').innerHTML = 'An error occurred while fetching results.';
        document.getElementById('results-container').style.display = 'block';
    });
}

const serverLinks = {
    'T3/Barley': 'https://barley.triticeaetoolbox.org/',
    'T3/Wheat': 'https://wheat.triticeaetoolbox.org/',
    'T3/Oat': 'https://oat.triticeaetoolbox.org/',
    // Add more mappings as needed
};

function displayResults(query, data) {
    currentSearchResults = data;
    currentSearchQuery = query;

    document.getElementById('search-term-display').textContent = query;

    // Display the results container
    document.getElementById('results-container').style.display = 'block';

    // Handle the results (grouped, count, etc.)
    const resultsCount = document.getElementById('results-count');
    const groupedResults = document.getElementById('grouped-results');
    resultsCount.innerHTML = data.length === 0 ? 'No results found.' : `${data.length} result(s) found`;
    groupedResults.innerHTML = ''; // Clear previous results

    // Create table for results
    const table = document.createElement('table');
    table.className = 'table table-striped table-bordered';
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Create table header
    const headerRow = document.createElement('tr');
    const resultHeader = document.createElement('th');
    resultHeader.textContent = 'Result';
    const serverHeader = document.createElement('th');
    serverHeader.textContent = 'Server';
    headerRow.appendChild(resultHeader);
    headerRow.appendChild(serverHeader);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Process and display results
    const groupedData = data.reduce((acc, item) => {
        if (!acc[item.server_name]) acc[item.server_name] = [];
        acc[item.server_name].push(item);
        return acc;
    }, {});

    // Populate the server filter checkboxes
    const serverFilterContainer = document.getElementById('serverFilterContainer');
    serverFilterContainer.innerHTML = '';
    Object.keys(groupedData).forEach(serverName => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `filter-${serverName}`;
        checkbox.value = serverName;
        checkbox.checked = true;
        checkbox.addEventListener('change', filterResultsByServer);

        const label = document.createElement('label');
        label.htmlFor = `filter-${serverName}`;
        label.textContent = serverName;

        const container = document.createElement('div');
        container.className = 'form-check form-check-inline';
        container.appendChild(checkbox);
        container.appendChild(label);

        serverFilterContainer.appendChild(container);
    });

    for (const [serverName, samples] of Object.entries(groupedData)) {
        samples.forEach(sample => {
            const row = document.createElement('tr');
            const resultCell = document.createElement('td');
            const serverCell = document.createElement('td');

            let url = '';

            if (sample.germplasmDbId) {
                url = `/details/germplasm/${sample.germplasmDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(serverName)}`;
                resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.defaultDisplayName} (${sample.species})</a>`;
            } else if (sample.traitDbId) {
                url = `/details/trait/${sample.traitDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(serverName)}`;
                resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.traitName} (Trait ID: ${sample.traitDbId})</a>`;
            } else if (sample.trialDbId) {
                url = `/details/trial/${sample.trialDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(serverName)}`;
                resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.trialName} (Trial ID: ${sample.trialDbId})</a>`;
            }

            // Link the server name to its URL
            if (serverLinks[serverName]) {
                serverCell.innerHTML = `<a href="${serverLinks[serverName]}" target="_blank">${serverName}</a>`;
            } else {
                serverCell.textContent = serverName;
            }

            row.appendChild(resultCell);
            row.appendChild(serverCell);
            tbody.appendChild(row);
        });
    }

    table.appendChild(tbody);
    groupedResults.appendChild(table);
}


function filterResultsByServer() {
    const selectedServers = Array.from(document.querySelectorAll('#serverFilterContainer input[type="checkbox"]:checked')).map(cb => cb.value);
    const filteredResults = currentSearchResults.filter(item => selectedServers.includes(item.server_name));
    displayResults(currentSearchQuery, filteredResults);
}

document.addEventListener('DOMContentLoaded', function() {
    const showResults = sessionStorage.getItem('showResults');
    const searchResults = sessionStorage.getItem('searchResults');
    const searchQuery = sessionStorage.getItem('searchQuery');

    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        if (showResults === 'true' && searchResults) {
            // Display stored results
            displayResults(searchQuery, JSON.parse(searchResults));

            // Clear session storage
            sessionStorage.removeItem('showResults');
            sessionStorage.removeItem('searchResults');
            sessionStorage.removeItem('searchQuery');
        } else {
            resultsContainer.style.display = 'none';
        }
    } else {
        console.error('Element with ID "results-container" not found.');
    }
});



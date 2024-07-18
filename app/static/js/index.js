document.querySelectorAll('.single-radio').forEach((radio) => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('.single-radio').forEach((rb) => {
            if (rb !== radio) rb.checked = false;
        });
    });
});

function validateForm() {
    const searchBox = document.getElementById('searchBox');
    const errorQuery = document.getElementById('errorQuery');
    const errorCheckbox = document.getElementById('errorCheckbox');
    const errorRadio = document.getElementById('errorRadio');
    const checkboxes = document.querySelectorAll('input[name="servers[]"]:checked');
    const radios = document.querySelectorAll('input[name="search_for"]:checked');

    let valid = true;
    const searchQuery = searchBox.value.trim();
    const regex = /^[a-zA-Z0-9\s]+$/;

    if (!regex.test(searchQuery)) {
        if(!alert('Invalid input. Only alphanumeric characters and spaces are allowed.')){window.location.reload();}
        event.preventDefault();
        return false;
    }

    errorQuery.style.display = searchQuery === '' ? 'block' : 'none';
    errorCheckbox.style.display = checkboxes.length === 0 ? 'block' : 'none';
    errorRadio.style.display = radios.length === 0 ? 'block' : 'none';

    return valid;
}

// Keyword search for Datasets
document.getElementById('datasetSearch').addEventListener('input', function() {
    let filter = this.value.toLowerCase();
    let labels = document.getElementById('datasetContainer').getElementsByTagName('label');
    Array.from(labels).forEach(label => {
        let text = label.textContent || label.innerText;
        label.style.display = text.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
    });
});

// Keyword search for Search for
document.getElementById('searchForSearch').addEventListener('input', function() {
    let filter = this.value.toLowerCase();
    let labels = document.getElementById('searchForContainer').getElementsByTagName('label');
    Array.from(labels).forEach(label => {
        let text = label.textContent || label.innerText;
        label.style.display = text.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
    });
});

// Clear all datasets
document.getElementById('clearDatasets').addEventListener('click', function() {
    document.querySelectorAll('input[name="servers[]"]').forEach(cb => cb.checked = false);
    updateSelectedFilters();
});

// Toggle filter tags
function toggleFilter(event) {
    updateSelectedFilters();
    updateClearButtonVisibility();
}

// Clear button visibility function
function updateClearButtonVisibility() {
    const clearButton = document.getElementById('clearDatasets');
    const selectedDatasets = document.querySelectorAll('input[name="servers[]"]:checked');

    clearButton.style.display = selectedDatasets.length > 0 ? 'block' : 'none';
}

// Update selected filters display
function updateSelectedFilters() {
    const selectedFiltersContainer = document.getElementById('selectedFilters');
    selectedFiltersContainer.innerHTML = '';

    // Get selected datasets
    const selectedDatasets = Array.from(document.querySelectorAll('input[name="servers[]"]:checked'))
        .map(cb => cb.value);
    selectedDatasets.forEach(dataset => {
        addFilterTag(dataset, 'servers[]');
    });
    updateClearButtonVisibility();
}

// Add filter tag to display
function addFilterTag(filter, name) {
    const selectedFiltersContainer = document.getElementById('selectedFilters');
    const tag = document.createElement('div');
    tag.className = 'filter-tag';
    tag.innerHTML = `<span>${filter}</span> <button onclick="removeFilter('${filter}', '${name}')">&times;</button>`;
    selectedFiltersContainer.appendChild(tag);
}

// Remove filter
function removeFilter(filter, name) {
    const inputs = document.querySelectorAll(`input[name="${name}"]`);
    inputs.forEach(input => {
        if (input.value === filter) {
            input.checked = false;
        }
    });
    updateSelectedFilters();
}
document.getElementById('search-button').addEventListener('click', function() {
    performSearch();
});

function performSearch(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Validate the form
    //const query = document.getElementById('searchBox').value;
    const servers = document.querySelectorAll('input[name="servers[]"]:checked');
    const searchFor = document.querySelectorAll('input[name="search_for"]:checked');

    let valid = true;
    const query = searchBox.value.trim();
    const regex = /^[a-zA-Z0-9\s]+$/;

    if (!regex.test(query)) {
        if(!alert('Invalid input. Only alphanumeric characters and spaces are allowed.')){window.location.reload();}
        event.preventDefault();
        clearInput();
        return false;
    }

    if (!query) {
    document.getElementById('errorQuery').style.display = 'block';
    valid = false;
    } else {
    document.getElementById('errorQuery').style.display = 'none';
    }

    if (servers.length === 0) {
    document.getElementById('errorCheckbox').style.display = 'block';
    valid = false;
    } else {
    document.getElementById('errorCheckbox').style.display = 'none';
    }

    if (searchFor.length === 0) {
    document.getElementById('errorRadio').style.display = 'block';
    valid = false;
    } else {
    document.getElementById('errorRadio').style.display = 'none';
    }

    if (!valid) return;

    // Prepare data to send in the POST request
    const formData = new FormData();
    formData.append('query', query);
    servers.forEach(server => {
    formData.append('servers[]', server.value);
    });
    searchFor.forEach(item => {
    formData.append('search_for', item.value);
    });

    fetch('/search', {
    method: 'POST',
    body: formData
    })
    .then(response => response.json())
    .then(data => {
    const resultsContainer = document.getElementById('results-container');
    const searchTermDisplay = document.getElementById('search-term-display');
    const resultsCount = document.getElementById('results-count');
    const groupedResults = document.getElementById('grouped-results');

    // Update the search term display
    searchTermDisplay.textContent = query;

    // Clear previous results
    resultsCount.innerHTML = '';
    groupedResults.innerHTML = '';

    if (data.length === 0) {
        resultsCount.textContent = 'No results found.';
    } else {
        const resultCount = data.length;
        resultsCount.textContent = `${resultCount} result(s) found`;

        // Group results by server_name
        const groupedData = data.reduce((acc, item) => {
            if (!acc[item.server_name]) {
                acc[item.server_name] = [];
            }
            acc[item.server_name].push(item);
            return acc;
        }, {});

        for (const [serverName, samples] of Object.entries(groupedData)) {
            const resultsList = document.createElement('ul');
            resultsList.className = 'results-list';
            
            samples.forEach(sample => {
                const listItem = document.createElement('li');
                let url = '';
                
                if (sample.germplasmDbId) {
                    url = `/details/germplasm/${sample.germplasmDbId}?base_url=${encodeURIComponent(sample.base_url)}`;
                    listItem.innerHTML = `<a href="#" data-url="${url}"><span class="highlight">${sample.defaultDisplayName}</span> (${sample.species})</a> <span class="server-name">from ${serverName}</span>`;
                } else if (sample.traitDbId) {
                    url = `/details/trait/${sample.traitDbId}?base_url=${encodeURIComponent(sample.base_url)}`;
                    listItem.innerHTML = `<a href="#" data-url="${url}"><span class="highlight">${sample.traitName}</span> (Trait ID: ${sample.traitDbId})</a> <span class="server-name">from ${serverName}</span>`;
                } else if (sample.trialDbId) {
                    url = `/details/trial/${sample.trialDbId}?base_url=${encodeURIComponent(sample.base_url)}`;
                    listItem.innerHTML = `<a href="#" data-url="${url}"><span class="highlight">${sample.trialName}</span> (Trial ID: ${sample.trialDbId})</a> <span class="server-name">from ${serverName}</span>`;
                }

                listItem.querySelector('a').addEventListener('click', function(event) {
                    event.preventDefault();
                    window.location.href = this.getAttribute('data-url');
                });

                resultsList.appendChild(listItem);
            });

            groupedResults.appendChild(resultsList);
        }
}

// Show the results container
resultsContainer.style.display = 'block';
})
.catch(error => {
console.error('Error fetching search results:', error);
const resultsContainer = document.getElementById('results-container');
resultsContainer.innerHTML = 'An error occurred while fetching results.';
resultsContainer.style.display = 'block';
});
}

function clearInput() { 
    document.getElementById("search-form").reset();
} 
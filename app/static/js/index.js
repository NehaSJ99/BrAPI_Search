// Single Radio Button Logic
document.querySelectorAll('.single-radio').forEach((radio) => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('.single-radio').forEach((rb) => {
            if (rb !== radio) rb.checked = false;
        });
    });
});

// Form Validation
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
        alert('Invalid input. Only alphanumeric characters and spaces are allowed.');
        window.location.reload();
        return false;
    }

    errorQuery.style.display = searchQuery === '' ? 'block' : 'none';
    errorCheckbox.style.display = checkboxes.length === 0 ? 'block' : 'none';
    errorRadio.style.display = radios.length === 0 ? 'block' : 'none';

    return valid;
}

// Keyword Search for Datasets
document.getElementById('datasetSearch').addEventListener('input', function() {
    let filter = this.value.toLowerCase();
    let labels = document.getElementById('datasetContainer').getElementsByTagName('label');
    Array.from(labels).forEach(label => {
        let text = label.textContent || label.innerText;
        label.style.display = text.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
    });
});

// Keyword Search for Data Types
document.getElementById('searchForSearch').addEventListener('input', function() {
    let filter = this.value.toLowerCase();
    let labels = document.getElementById('searchForContainer').getElementsByTagName('label');
    Array.from(labels).forEach(label => {
        let text = label.textContent || label.innerText;
        label.style.display = text.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
    });
});

// Clear All Datasets
document.getElementById('clearDatasets').addEventListener('click', function() {
    document.querySelectorAll('input[name="servers[]"]').forEach(cb => cb.checked = false);
    updateSelectedFilters();
});

// Toggle Filter Tags
function toggleFilter(event) {
    updateSelectedFilters();
    updateClearButtonVisibility();
}

// Update Clear Button Visibility
function updateClearButtonVisibility() {
    const clearButton = document.getElementById('clearDatasets');
    const selectedDatasets = document.querySelectorAll('input[name="servers[]"]:checked');

    clearButton.style.display = selectedDatasets.length > 0 ? 'block' : 'none';
}

// Update Selected Filters Display
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

// Add Filter Tag to Display
function addFilterTag(filter, name) {
    const selectedFiltersContainer = document.getElementById('selectedFilters');
    const tag = document.createElement('div');
    tag.className = 'filter-tag';
    tag.innerHTML = `<span>${filter}</span> <button type="button" class="btn btn-danger btn-sm" onclick="removeFilter('${filter}', '${name}')">&times;</button>`;
    selectedFiltersContainer.appendChild(tag);
}

// Remove Filter
function removeFilter(filter, name) {
    const inputs = document.querySelectorAll(`input[name="${name}"]`);
    inputs.forEach(input => {
        if (input.value === filter) {
            input.checked = false;
        }
    });
    updateSelectedFilters();
}

// Clear Input Fields
function clearInput() {
    document.getElementById("search-form").reset();
    updateSelectedFilters();
    updateClearButtonVisibility();
    
    // Hide results container after clearing
    document.getElementById('results-container').style.display = 'none';
}

// Search Button Event Listener
const searchButton = document.getElementById('search-button');
if (searchButton) {
    searchButton.addEventListener('click', function(event) {
        performSearch(event);
    });
} else {
    console.error('Element with ID "search-button" not found.');
}

function setExample(example, databases, dataType) {
    const searchBox = document.getElementById('searchBox');
    searchBox.value = example;

    // Clear all checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);

    // Check the specified databases
    databases.forEach(db => {
        const checkbox = document.querySelector(`input[name="servers[]"][value="${db}"]`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });

    // Clear all radio buttons
    const radioButtons = document.querySelectorAll('input[name="search_for"]');
    radioButtons.forEach(radio => radio.checked = false);

    // Check the specified data type radio button
    const radioButton = document.querySelector(`input[name="search_for"][value="${dataType}"]`);
    if (radioButton) {
        radioButton.checked = true;
    }
}






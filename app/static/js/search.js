// Initialize variables
let currentSearchResults = [];
let currentSearchQuery = '';
let resultsPerPage = 10; // Number of results per page
let currentPage = 1; // Current page number
let isSorted = false; // Initial sorting state
let allFilterOptions = {}; // Store all unique filter options
let originalSearchResults = []; // Add this line to store the original results

const serverLinks = {
    'T3/Barley': 'https://barley.triticeaetoolbox.org/',
    'T3/Wheat': 'https://wheat.triticeaetoolbox.org/',
    'T3/Oat': 'https://oat.triticeaetoolbox.org/',
    'IPK Gatersleben': 'https://www.ipk-gatersleben.de/',
    'URGI' : 'https://urgi.versailles.inra.fr/',
    'GrainGenes' : 'https://graingenes.org/GG3/',
    // Add more mappings as needed
};

// Functions to show and hide the spinner
function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'flex';
}

function hideSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function performSearch(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    if (!validateForm()) {
        return;
    }

    // Show the spinner before starting the search
    showSpinner();

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
        if (data && data.results) {
            // Store results in sessionStorage
            sessionStorage.setItem('searchResults', JSON.stringify(data.results));
            sessionStorage.setItem('searchQuery', formData.get('query'));
            sessionStorage.setItem('showResults', 'true'); // Flag to show results

            // Update the search term display and results
            displayResults(formData.get('query'), data.results);
        } else {
            throw new Error("Invalid response structure");
        }
    })
    .catch(error => {
        console.error('Error fetching search results:', error);
        document.getElementById('results-container').innerHTML = 'An error occurred while fetching results.';
        document.getElementById('results-container').style.display = 'block';
    })
    .finally(() => {
        // Hide the spinner after the search is complete, regardless of success or failure
        hideSpinner();
    });
}

// Functions to show and hide the spinner
function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'flex';
}

function hideSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

// Modify displayResults to include a call to populateDatabaseFilterOptions
function displayResults(query, data) {
    currentSearchResults = data;
    currentSearchQuery = query;

    // Store the original data if it hasn't been stored yet
    if (originalSearchResults.length === 0) {
        originalSearchResults = [...data]; // Use spread operator to copy array
    }

    console.log('Total count:', data.totalCount); // Check total count
    console.log('Total Results:', data.length);

    // Display the results container
    document.getElementById('results-container').style.display = 'block';

    // Update the search term display
    const searchTermDisplay = document.getElementById('search-term-display');
    if (searchTermDisplay) {
        searchTermDisplay.textContent = query || 'No query entered';
    } else {
        console.error('Element with ID "search-term-display" not found.');
    }

    // Handle the results (count, etc.)
    const resultsCount = document.getElementById('results-count');
    resultsCount.innerHTML = data.length === 0 ? 'No results found.' : `${data.length} result(s) found`;

    // Sort results if isSorted is true
    const resultsToDisplay = isSorted ? sortResults(data) : data;

    // Display results for the current page
    const startIndex = (currentPage - 1) * resultsPerPage;
    const endIndex = Math.min(startIndex + resultsPerPage, data.length);
    const currentResults = resultsToDisplay .slice(startIndex, endIndex);

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

    // Process and display current results
    currentResults.forEach(sample => {
        const row = document.createElement('tr');
        const resultCell = document.createElement('td');
        const serverCell = document.createElement('td');

        let url = '';

        if (sample.germplasmDbId) {
            url = `/details/germplasm/${sample.germplasmDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(sample.server_name)}`;
            resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.germplasmDbId} (${sample.species})</a>`;
        } else if (sample.traitDbId) {
            url = `/details/trait/${sample.traitDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(sample.server_name)}`;
            resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.traitName} (Trait ID: ${sample.traitDbId})</a>`;
        } else if (sample.trialDbId) {
            url = `/details/trial/${sample.trialDbId}?base_url=${encodeURIComponent(sample.base_url)}&server_name=${encodeURIComponent(sample.server_name)}`;
            resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.trialName} (Trial ID: ${sample.trialDbId})</a>`;
        }

        // Link the server name to its URL
        if (serverLinks[sample.server_name]) {
            serverCell.innerHTML = `<a href="${serverLinks[sample.server_name]}" target="_blank">${sample.server_name}</a>`;
        } else {
            serverCell.textContent = sample.server_name;
        }

        row.appendChild(resultCell);
        row.appendChild(serverCell);
        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    document.getElementById('grouped-results').innerHTML = ''; // Clear previous results
    document.getElementById('grouped-results').appendChild(table);

    // Create and display pagination controls
    createPaginationControls(data.length);
}

function createPaginationControls(totalResults) {
    const paginationContainer = document.getElementById('pagination-controls');
    paginationContainer.innerHTML = ''; // Clear previous pagination controls

    const totalPages = Math.ceil(totalResults / resultsPerPage);

    // Create "Previous" button
    const prevButton = document.createElement('li');
    prevButton.className = 'page-item' + (currentPage === 1 ? ' disabled' : '');
    const prevLink = document.createElement('a');
    prevLink.href = '#';
    prevLink.className = 'page-link';
    prevLink.textContent = 'Previous';
    prevLink.addEventListener('click', function(event) {
        event.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            displayResults(currentSearchQuery, currentSearchResults);
        }
    });
    prevButton.appendChild(prevLink);
    paginationContainer.appendChild(prevButton);

    // Helper function to create a page number link
    function createPageLink(pageNumber) {
        const pageItem = document.createElement('li');
        pageItem.className = 'page-item' + (pageNumber === currentPage ? ' active' : '');
        const pageLink = document.createElement('a');
        pageLink.href = '#';
        pageLink.className = 'page-link';
        pageLink.textContent = pageNumber;
        pageLink.addEventListener('click', function(event) {
            event.preventDefault();
            currentPage = pageNumber;
            displayResults(currentSearchQuery, currentSearchResults);
        });
        pageItem.appendChild(pageLink);
        return pageItem;
    }

    // Create page number links
    if (totalPages <= 5) {
        // If there are 5 or fewer pages, show all page numbers
        for (let i = 1; i <= totalPages; i++) {
            paginationContainer.appendChild(createPageLink(i));
        }
    } else {
        // Show first page, first few pages, and last page
        paginationContainer.appendChild(createPageLink(1)); // First page

        if (currentPage > 4) {
            paginationContainer.appendChild(createPageLink('...'));
        }

        // Display a range of page numbers around the current page
        const startPage = Math.max(2, currentPage - 2);
        const endPage = Math.min(totalPages - 1, currentPage + 2);
        for (let i = startPage; i <= endPage; i++) {
            paginationContainer.appendChild(createPageLink(i));
        }

        if (currentPage < totalPages - 3) {
            paginationContainer.appendChild(createPageLink('...'));
        }

        paginationContainer.appendChild(createPageLink(totalPages)); // Last page
    }

    // Create "Next" button
    const nextButton = document.createElement('li');
    nextButton.className = 'page-item' + (currentPage === totalPages ? ' disabled' : '');
    const nextLink = document.createElement('a');
    nextLink.href = '#';
    nextLink.className = 'page-link';
    nextLink.textContent = 'Next';
    nextLink.addEventListener('click', function(event) {
        event.preventDefault();
        if (currentPage < totalPages) {
            currentPage++;
            displayResults(currentSearchQuery, currentSearchResults);
        }
    });
    nextButton.appendChild(nextLink);
    paginationContainer.appendChild(nextButton);
}

function filterResultsByDatabase() {
    const databaseFilter = document.getElementById('databaseFilter');
    const selectedOptions = Array.from(databaseFilter.selectedOptions).map(option => option.value);

    console.log('Selected filters:', selectedOptions); // Debug log

    // Filter results based on selected options
    const filteredResults = selectedOptions.includes('all') || selectedOptions.length === 0
        ? originalSearchResults
        : originalSearchResults.filter(result => selectedOptions.includes(result.server_name));

    console.log('Filtered results:', filteredResults); // Debug log

    // Display the filtered results
    displayResults(currentSearchQuery, filteredResults);
}


function populateDatabaseFilterOptions(data) {
    const databaseFilter = document.getElementById('databaseFilter');
    const databaseCounts = {};

    // Count the occurrences of each server
    data.forEach(result => {
        if (databaseCounts[result.server_name]) {
            databaseCounts[result.server_name]++;
        } else {
            databaseCounts[result.server_name] = 1;
        }
    });

    // Clear existing options
    databaseFilter.innerHTML = '<option value="all">Filter by Server</option>';

    // Add new options
    Object.keys(databaseCounts).forEach(server => {
        const option = document.createElement('option');
        option.value = server;
        option.textContent = `${server} (${databaseCounts[server]})`;
        databaseFilter.appendChild(option);
    });

    // Ensure only one event listener is attached
    const handleChange = () => {
        filterResultsByDatabase();
    };

    // Remove existing event listener to prevent multiple attachments
    databaseFilter.removeEventListener('change', handleChange);

    // Add event listener to handle selection changes
    databaseFilter.addEventListener('change', handleChange);
}


//sorting results alphabetically
function sortResults(data) {
    return data.slice().sort((a, b) => {
        // Handle cases where defaultDisplayName might be undefined
        const nameA = (a.defaultDisplayName || '').toLowerCase();
        const nameB = (b.defaultDisplayName || '').toLowerCase();

        if (nameA < nameB) return -1;
        if (nameA > nameB) return 1;
        return 0;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const showResults = sessionStorage.getItem('showResults');
    const searchResults = sessionStorage.getItem('searchResults');
    const searchQuery = sessionStorage.getItem('searchQuery');

    if (showResults === 'true' && searchResults) {
        const results = JSON.parse(searchResults);
        populateDatabaseFilterOptions(results); // Initialize filter options once
        displayResults(searchQuery, results);
    }

    // Handle sorting button
    const sortButton = document.getElementById('sort-button');
    if (sortButton) {
        sortButton.addEventListener('click', function() {
            // Toggle sorting state
            isSorted = !isSorted;

            // Retrieve results from sessionStorage
            const results = JSON.parse(sessionStorage.getItem('searchResults'));

            if (results) {
                // Display results with new sorting state
                displayResults(sessionStorage.getItem('searchQuery'), results);
            }
        });
    } else {
        console.error('Element with ID "sort-button" not found.');
    }

    // Attach event listener for database filter selection
    const databaseFilter = document.getElementById('databaseFilter');
    if (databaseFilter) {
        databaseFilter.addEventListener('change', filterResultsByDatabase);
    } else {
        console.error('Element with ID "databaseFilter" not found.');
    }
});


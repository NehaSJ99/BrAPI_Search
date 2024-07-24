// Initialize variables
let currentSearchResults = [];
let currentSearchQuery = '';
let resultsPerPage = 10; // Number of results per page
let currentPage = 1; // Current page number

const serverLinks = {
    'T3/Barley': 'https://barley.triticeaetoolbox.org/',
    'T3/Wheat': 'https://wheat.triticeaetoolbox.org/',
    'T3/Oat': 'https://oat.triticeaetoolbox.org/',
    // Add more mappings as needed
};

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
    });
}

function displayResults(query, data) {
    currentSearchResults = data;
    currentSearchQuery = query;

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

    // Display results for the current page
    const startIndex = (currentPage - 1) * resultsPerPage;
    const endIndex = Math.min(startIndex + resultsPerPage, data.length);
    const currentResults = data.slice(startIndex, endIndex);

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
            resultCell.innerHTML = `<a href="${url}" target="_blank">${sample.defaultDisplayName} (${sample.species})</a>`;
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


document.addEventListener('DOMContentLoaded', function() {
    const showResults = sessionStorage.getItem('showResults');
    const searchResults = sessionStorage.getItem('searchResults');
    const searchQuery = sessionStorage.getItem('searchQuery');

    if (showResults === 'true' && searchResults) {
        const results = JSON.parse(searchResults);
        displayResults(searchQuery, results);
    }
});

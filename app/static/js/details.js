document.addEventListener("DOMContentLoaded", function() {
    const query = "{{ query|e }}";
    if (query) {
        const elements = document.querySelectorAll(".detail-value td");
        elements.forEach(element => {
            const innerHTML = element.innerHTML;
            const regex = new RegExp(`(${query})`, 'gi');
            element.innerHTML = innerHTML.replace(regex, '<span class="highlight">$1</span>');
        });
    }

    // Make URLs clickable
    const urlPattern = /https?:\/\/[^\s]+/g;
    const detailElements = document.querySelectorAll(".detail-value td");
    detailElements.forEach(element => {
        element.innerHTML = element.innerHTML.replace(urlPattern, url => `<a href="${url}" target="_blank">${url}</a>`);
    });
});

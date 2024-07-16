document.addEventListener("DOMContentLoaded", function() {
    const query = "{{ query|e }}";
    if (query) {
        const elements = document.querySelectorAll(".detail-value");
        elements.forEach(element => {
            const innerHTML = element.innerHTML;
            const regex = new RegExp(`(${query})`, 'gi');
            element.innerHTML = innerHTML.replace(regex, '<span class="highlight">$1</span>');
        });
    }

    // Make URLs clickable
    const urlPattern = /https?:\/\/[^\s]+/g;
    const elements = document.querySelectorAll(".detail-value");
    elements.forEach(element => {
        element.innerHTML = element.innerHTML.replace(urlPattern, url => `<a href="${url}" target="_blank">${url}</a>`);
    });
});
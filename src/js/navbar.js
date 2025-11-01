// Navbar include script
function loadNavbar() {
    fetch('/frontend/templates/navbar.html')
        .then(response => response.text())
        .then(html => {
            // Find the navbar div and replace its content
            const navbarDiv = document.querySelector('.navbar');
            if (navbarDiv) {
                navbarDiv.innerHTML = html;
            }
        })
        .catch(error => console.error('Error loading navbar:', error));
}

// Load navbar when DOM is ready
document.addEventListener('DOMContentLoaded', loadNavbar);

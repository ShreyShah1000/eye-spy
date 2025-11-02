// Navbar include script
function loadNavbar() {
    fetch('/frontend/templates/navbar.html')
        .then(response => response.text())
        .then(html => {
            // Find the navbar div and replace its content
            const navbarDiv = document.querySelector('.navbar');
            if (navbarDiv) {
                navbarDiv.innerHTML = html;
                // Initialize theme after navbar is loaded
                updateTheme();
            }
        })
        .catch(error => console.error('Error loading navbar:', error));
}

// Theme management functions
function toggleMode() {
    document.body.classList.toggle('dark');
    setMode();
}

function setMode() {
    const isDark = document.body.classList.contains('dark');
    const iconText = isDark ? 'light_mode' : 'dark_mode';
    const mode = isDark ? 'dark' : 'light';

    const colorThemeEl = document.getElementById('color-theme');
    if (colorThemeEl) {
        colorThemeEl.innerText = iconText;
    }

    localStorage.setItem('theme', mode);
}

function updateTheme() {
    const savedTheme = localStorage.getItem('theme');
    const isDark = savedTheme === 'dark';

    if (isDark) {
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark');
    }

    // Update icon to reflect current state (opposite for toggle)
    const colorThemeEl = document.getElementById('color-theme');
    if (colorThemeEl) {
        colorThemeEl.innerText = isDark ? 'light_mode' : 'dark_mode';
    }
}

// Load navbar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    loadNavbar();
});

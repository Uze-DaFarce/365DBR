// script.js - Interactive fun stuff for Day By Day Kids

document.addEventListener('DOMContentLoaded', () => {

    // Bible Click Interaction (Closed -> Open -> Closed)
    const bibleToggle = document.querySelector('.bible-toggle');
    if (bibleToggle) {
        const closedImg = bibleToggle.querySelector('.closed');
        const openImg = bibleToggle.querySelector('.open');

        bibleToggle.addEventListener('click', () => {
            // Add a little bounce effect on click
            bibleToggle.style.transform = 'scale(0.9)';
            setTimeout(() => {
                bibleToggle.style.transform = 'scale(1)';

                // Toggle visibility
                if (closedImg.style.display !== 'none') {
                    closedImg.style.display = 'none';
                    openImg.style.display = 'block';
                } else {
                    closedImg.style.display = 'block';
                    openImg.style.display = 'none';
                }
            }, 150);
        });
    }

    // Intersection Observer for scroll animations (lazy triggering of animations)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.2
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Remove animation class and add it back to trigger restart if needed
                // Currently CSS handles initial load animations, but this can be expanded
                entry.target.style.opacity = 1;
            }
        });
    }, observerOptions);

    const sections = document.querySelectorAll('.section');
    sections.forEach(sec => observer.observe(sec));
});
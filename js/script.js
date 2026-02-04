// Simple success overlay for forms
document.querySelectorAll('a[href*="docs.google.com"]').forEach(a => {
  a.addEventListener('click', () => {
    const o = document.createElement('div');
    o.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(64,27,81,0.95);color:white;z-index:9999;display:flex;align-items:center;justify-content:center;font-size:18px;text-align:center;padding:20px;';

    // Security enhancement: Use DOM creation instead of innerHTML to prevent XSS risks
    const container = document.createElement('div');

    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '40px';
    emojiDiv.style.marginBottom = '12px';
    emojiDiv.textContent = '🙏';
    container.appendChild(emojiDiv);

    const text1 = document.createTextNode('Thank you! We will review your message and reply soon.');
    container.appendChild(text1);

    container.appendChild(document.createElement('br'));

    const text2 = document.createTextNode('Typically next business day.');
    container.appendChild(text2);

    o.appendChild(container);

    o.onclick = () => o.remove();
    document.body.appendChild(o);
    setTimeout(() => o.remove(), 8000);
  });
});

document.getElementById('copyright').textContent = `© 2024-${new Date().getFullYear()} Mt. Sinai LLC. All rights reserved. | Serving God through excellence in business.`;

// Reviews Toggle Logic
const toggleBtn = document.getElementById('toggle-reviews-btn');
const reviewsContainer = document.getElementById('more-reviews');

if (toggleBtn && reviewsContainer) {
  toggleBtn.addEventListener('click', () => {
    const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';

    if (!isExpanded) {
      // EXPAND
      reviewsContainer.classList.remove('hidden');
      // Small timeout to allow display:block to apply before animating
      setTimeout(() => {
          reviewsContainer.classList.add('reviews-expanded');
      }, 10);
      toggleBtn.textContent = 'Show Less Client Stories';
      toggleBtn.setAttribute('aria-expanded', 'true');
    } else {
      // COLLAPSE
      reviewsContainer.classList.remove('reviews-expanded');
      toggleBtn.textContent = 'Read More Client Stories';
      toggleBtn.setAttribute('aria-expanded', 'false');

      // Wait for transition to finish before hiding
      reviewsContainer.addEventListener('transitionend', function() {
        if (toggleBtn.getAttribute('aria-expanded') === 'false') {
          reviewsContainer.classList.add('hidden');
        }
      }, { once: true });
    }
  });
}

// Active Nav State logic
const navLinks = document.querySelectorAll('nav a');
// Map nav links to their target elements
const navTargets = Array.from(navLinks).map(link => {
  const id = link.getAttribute('href').substring(1);
  return {
    link: link,
    target: document.getElementById(id)
  };
}).filter(item => item.target !== null);

const backToTopBtn = document.getElementById('back-to-top');

// ⚡ Bolt: Optimize Scroll Handling
// Throttling scroll events with requestAnimationFrame to reduce main thread blocking
// and minimizing DOM updates to prevent layout thrashing.
let isTicking = false;
let lastActiveLink = null;
let isBackToTopVisible = false;

function onScroll() {
  const currentScrollY = window.scrollY;
  if (!isTicking) {
    window.requestAnimationFrame(() => {
      updateScrollState(currentScrollY);
      isTicking = false;
    });
    isTicking = true;
  }
}

function updateScrollState(scrollY) {
  // 1. Active Nav State
  const offset = 120; // Header height + buffer
  let activeLink = null;

  // Find the last section that has been passed
  navTargets.forEach(item => {
    if (scrollY >= item.target.offsetTop - offset) {
      activeLink = item.link;
    }
  });

  // Only update DOM if active link changed
  if (activeLink !== lastActiveLink) {
    navLinks.forEach(link => {
      if (link === activeLink) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.classList.remove('active');
        link.removeAttribute('aria-current');
      }
    });
    lastActiveLink = activeLink;
  }

  // 2. Back to Top Button Visibility
  if (backToTopBtn) {
    const shouldBeVisible = scrollY > 500;
    if (shouldBeVisible !== isBackToTopVisible) {
      if (shouldBeVisible) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
      isBackToTopVisible = shouldBeVisible;
    }
  }
}

window.addEventListener('scroll', onScroll, { passive: true });

// Initial check on load
updateScrollState(window.scrollY);

if (backToTopBtn) {
  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

// Simple success overlay for forms
document.querySelectorAll('a[href*="docs.google.com"]').forEach(trigger => {
  trigger.addEventListener('click', () => {
    const o = document.createElement('div');
    // Added accessibility roles and tabindex for focus management
    o.setAttribute('role', 'alertdialog');
    o.setAttribute('aria-modal', 'true');
    o.setAttribute('tabindex', '0');
    o.setAttribute('aria-label', 'Form Handoff: Opening secure Google Form. Press Escape to dismiss.');

    // Added cursor: pointer to indicate interactivity
    o.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(64,27,81,0.95);color:white;z-index:9999;display:flex;align-items:center;justify-content:center;font-size:18px;text-align:center;padding:20px;cursor:pointer;';

    // Security enhancement: Use DOM creation instead of innerHTML to prevent XSS risks
    const container = document.createElement('div');

    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '40px';
    emojiDiv.style.marginBottom = '12px';
    emojiDiv.textContent = '📝';
    container.appendChild(emojiDiv);

    const text1 = document.createTextNode('Opening Secure Form...');
    container.appendChild(text1);

    container.appendChild(document.createElement('br'));

    const text2 = document.createTextNode('Please complete your request in the new tab.');
    container.appendChild(text2);

    o.appendChild(container);

    const dismiss = () => {
      o.remove();
      // Restore focus to the trigger element
      trigger.focus();
    };

    o.onclick = dismiss;

    // Handle keyboard dismissal
    o.onkeydown = (e) => {
      if (['Escape', 'Enter', ' '].includes(e.key)) {
        e.preventDefault();
        dismiss();
      }
    };

    document.body.appendChild(o);
    o.focus(); // Set focus to overlay immediately

    setTimeout(() => {
      if (document.body.contains(o)) dismiss();
    }, 8000);
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

// ⚡ Bolt: Cache offsets to prevent reflow during scroll
let sectionOffsets = [];

// ⚡ Bolt: Debounce function to limit execution frequency
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

function updateOffsets() {
  sectionOffsets = navTargets.map(item => ({
    link: item.link,
    offset: item.target.offsetTop
  }));
}

// Initial cache
updateOffsets();

// ⚡ Bolt: Debounce resize handler to prevent layout thrashing
const debouncedUpdateOffsets = debounce(updateOffsets, 100);

// Update offsets when layout changes (e.g. reviews toggle)
if (window.ResizeObserver) {
  new ResizeObserver(debouncedUpdateOffsets).observe(document.body);
} else {
  // Fallback
  window.addEventListener('resize', debouncedUpdateOffsets);
}

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

  // Find the last section that has been passed (Iterate backwards for efficiency)
  for (let i = sectionOffsets.length - 1; i >= 0; i--) {
    if (scrollY >= sectionOffsets[i].offset - offset) {
      activeLink = sectionOffsets[i].link;
      break;
    }
  }

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
    // Move focus to the top of the page (Logo) to prevent focus trap
    // as the button becomes invisible after scrolling
    const logo = document.querySelector('.logo');
    if (logo) {
      logo.focus({ preventScroll: true });
    }
  });
}

// Helper to create SVG elements
function createSVG(type) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  svg.setAttribute('width', '18');
  svg.setAttribute('height', '18');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');

  if (type === 'check') {
    const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    polyline.setAttribute('points', '20 6 9 17 4 12');
    svg.appendChild(polyline);
  } else if (type === 'copy') {
    svg.classList.add('copy-icon');
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', '9');
    rect.setAttribute('y', '9');
    rect.setAttribute('width', '13');
    rect.setAttribute('height', '13');
    rect.setAttribute('rx', '2');
    rect.setAttribute('ry', '2');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1');
    svg.appendChild(rect);
    svg.appendChild(path);
  }
  return svg;
}

// Copy to Clipboard logic
const copyBtn = document.querySelector('.copy-btn');
if (copyBtn) {
  copyBtn.addEventListener('click', () => {
    const email = 'truth@mt-sin.ai';
    navigator.clipboard.writeText(email)
      .then(() => {
        copyBtn.classList.add('copied');
        copyBtn.setAttribute('aria-label', 'Email copied');

        // Clear existing content safely
        while (copyBtn.firstChild) {
          copyBtn.removeChild(copyBtn.firstChild);
        }

        // Add Check Icon
        copyBtn.appendChild(createSVG('check'));

        // Add Tooltip text
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip-text';
        tooltip.textContent = 'Copied!';
        copyBtn.appendChild(tooltip);

        setTimeout(() => {
          copyBtn.classList.remove('copied');
          copyBtn.setAttribute('aria-label', 'Copy email address');

          // Clear and restore original icon
          while (copyBtn.firstChild) {
            copyBtn.removeChild(copyBtn.firstChild);
          }
          copyBtn.appendChild(createSVG('copy'));
        }, 2000);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
      });
  });
}

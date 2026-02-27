// Simple success overlay for forms
// Security enhancement: Use stricter selector to prevent matching malicious links (e.g. evil.com?ref=docs.google.com) and limit to forms only
// Sentinel: Added support for http protocol to prevent bypassing the overlay with insecure links
document.querySelectorAll('a[href^="https://docs.google.com/forms/"], a[href^="http://docs.google.com/forms/"]').forEach(trigger => {
  trigger.addEventListener('click', () => {
    const o = document.createElement('div');
    // Added accessibility roles and tabindex for focus management
    o.setAttribute('role', 'alertdialog');
    o.setAttribute('aria-modal', 'true');
    o.setAttribute('tabindex', '0');
    o.setAttribute('aria-label', 'Form Handoff: Opening secure Google Form. Press Escape to dismiss.');

    // Added cursor: pointer to indicate interactivity
    o.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(64,27,81,0.95);color:white;z-index:9999;display:flex;align-items:center;justify-content:center;font-size:18px;text-align:center;padding:20px;cursor:pointer;';

    // 🎨 Palette: Add accessible Close Button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.setAttribute('aria-label', 'Close');
    // Enlarge button and add semi-transparent circle for maximum visibility
    closeBtn.style.cssText = 'position:absolute;top:32px;right:32px;background:rgba(0,0,0,0.5);border:2px solid rgba(255,255,255,0.5);color:white;font-size:48px;cursor:pointer;padding:0;line-height:1;width:80px;height:80px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s ease;box-shadow: 0 4px 12px rgba(0,0,0,0.3);';

    // Add hover effect via JS since we are using inline styles
    closeBtn.onmouseenter = () => {
      closeBtn.style.backgroundColor = 'rgba(255,255,255,0.2)';
      closeBtn.style.transform = 'scale(1.1)';
    };
    closeBtn.onmouseleave = () => {
      closeBtn.style.backgroundColor = 'rgba(0,0,0,0.5)';
      closeBtn.style.transform = 'scale(1)';
    };

    // Focus style for keyboard accessibility
    closeBtn.onfocus = () => closeBtn.style.outline = '2px solid white';
    closeBtn.onblur = () => closeBtn.style.outline = 'none';

    o.appendChild(closeBtn);

    // Security enhancement: Use DOM creation instead of innerHTML to prevent XSS risks
    const container = document.createElement('div');
    // Ensure description is linked for accessibility
    const descId = 'form-handoff-desc';
    container.id = descId;
    o.setAttribute('aria-describedby', descId);

    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '40px';
    emojiDiv.style.marginBottom = '12px';
    emojiDiv.textContent = '📝';
    emojiDiv.setAttribute('aria-hidden', 'true'); // Hide decorative emoji from screen readers
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

      // 🎨 Palette: Move focus to new content for screen readers
      reviewsContainer.setAttribute('tabindex', '-1');
      reviewsContainer.style.outline = 'none';
      reviewsContainer.focus();
    } else {
      // COLLAPSE
      // 🎨 Palette: Scroll back to the toggle button to maintain context
      // This prevents the user from being stranded in empty space when content shrinks
      toggleBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });

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
// ⚡ Bolt: Cache document dimensions to avoid layout thrashing on scroll
let cachedDocHeight = 0;
let cachedWinHeight = 0;

// ⚡ Bolt: Debounce function to limit execution frequency
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

function updateDimensions() {
  sectionOffsets = navTargets.map(item => ({
    link: item.link,
    offset: item.target.offsetTop
  }));
  cachedWinHeight = document.documentElement.clientHeight;
  // Calculate the total scrollable height
  cachedDocHeight = document.documentElement.scrollHeight - cachedWinHeight;
}

// Initial cache
updateDimensions();

// ⚡ Bolt: Recalculate offsets after fonts load to ensure accuracy (prevents scroll spy issues from FOUT)
if (document.fonts) {
  document.fonts.ready.then(updateDimensions);
}

// ⚡ Bolt: Debounce resize handler to prevent layout thrashing
const debouncedUpdateDimensions = debounce(updateDimensions, 100);

// Update offsets when layout changes (e.g. reviews toggle)
// ⚡ Bolt: Use explicit event listeners instead of observing the entire body to prevent layout thrashing
window.addEventListener('resize', debouncedUpdateDimensions);

if (reviewsContainer) {
  reviewsContainer.addEventListener('transitionend', (e) => {
    // Only update when the height transition completes
    if (e.propertyName === 'grid-template-rows') {
      debouncedUpdateDimensions();
    }
  });
}

const backToTopBtn = document.getElementById('back-to-top');
// ⚡ Bolt: Cache progress bar to avoid repeated DOM lookups
const progressBar = document.getElementById('scroll-progress');

// ⚡ Bolt: Optimize Scroll Handling
// Throttling scroll events with requestAnimationFrame to reduce main thread blocking
// and minimizing DOM updates to prevent layout thrashing.
let isTicking = false;
let lastActiveLink = null;
let isBackToTopVisible = false;

function onScroll() {
  if (!isTicking) {
    window.requestAnimationFrame(() => {
      updateScrollState();
      isTicking = false;
    });
    isTicking = true;
  }
}

function updateScrollState() {
  const scrollY = window.scrollY;
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

        // 🎨 Palette: Ensure active link is visible in scrollable mobile nav
        link.scrollIntoView({
          behavior: 'smooth',
          inline: 'center',
          block: 'nearest'
        });
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

  // 3. Scroll Progress Bar
  // ⚡ Bolt: Use cached dimensions and transform instead of width to prevent layout thrashing
  if (progressBar) {
    let scaleX = 0;
    if (cachedDocHeight > 0) {
      scaleX = scrollY / cachedDocHeight;
      // Clamp between 0 and 1
      scaleX = Math.max(0, Math.min(1, scaleX));
    }
    progressBar.style.transform = `scaleX(${scaleX})`;
  }
}

window.addEventListener('scroll', onScroll, { passive: true });

// Initial check on load
updateScrollState();

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
const copyBtns = document.querySelectorAll('.copy-btn');
copyBtns.forEach(copyBtn => {
  copyBtn.addEventListener('click', () => {
    // 🎨 Palette: Prevent rapid re-clicks to avoid race conditions
    if (copyBtn.classList.contains('copied')) return;

    const textToCopy = copyBtn.getAttribute('data-copy-text');
    if (!textToCopy) return;

    // 🎨 Palette: Add haptic feedback for mobile delight
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }

    // Store original state for restoration
    const originalLabel = copyBtn.getAttribute('aria-label');
    const tooltip = copyBtn.querySelector('.tooltip-text');
    const originalTooltipText = tooltip ? tooltip.textContent : '';

    navigator.clipboard.writeText(textToCopy)
      .then(() => {
        const icon = copyBtn.querySelector('svg');

        copyBtn.classList.add('copied');
        copyBtn.setAttribute('aria-label', 'Copied!');

        // Update Icon
        if (icon) {
          icon.replaceWith(createSVG('check'));
        }

        // Update Tooltip Text
        if (tooltip) {
          tooltip.textContent = 'Copied!';
        }

        setTimeout(() => {
          copyBtn.classList.remove('copied');
          // Restore original label
          if (originalLabel) {
            copyBtn.setAttribute('aria-label', originalLabel);
          }

          // Restore Icon
          const currentIcon = copyBtn.querySelector('svg');
          if (currentIcon) {
            currentIcon.replaceWith(createSVG('copy'));
          }

          // Restore Tooltip Text
          if (tooltip) {
            tooltip.textContent = originalTooltipText;
          }
        }, 2000);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
        // 🎨 Palette: Provide visual feedback on failure
        if (tooltip) {
            const oldText = tooltip.textContent;
            tooltip.textContent = 'Failed';
            copyBtn.classList.add('error');
            setTimeout(() => {
                tooltip.textContent = oldText;
                copyBtn.classList.remove('error');
            }, 2000);
        }
      });
  });
});

// 🎨 Palette: Scroll Reveal Animation
const observerOptions = {
  root: null,
  rootMargin: '50px',
  threshold: 0.1
};

const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const target = entry.target;
      target.classList.add('is-visible');
      observer.unobserve(target);

      // Clean up classes after animation to prevent conflicts with hover effects
      target.addEventListener('transitionend', () => {
        target.classList.remove('reveal-on-scroll', 'is-visible');
      }, { once: true });
    }
  });
}, observerOptions);

// Only init animation if user prefers motion
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReducedMotion) {
  const revealElements = document.querySelectorAll('.service-card, .project-card, .package-card, .team-member, .review-card, .contact-info');

  revealElements.forEach(el => {
    // Only animate elements that are NOT already in the viewport
    const rect = el.getBoundingClientRect();
    const isAlreadyVisible = rect.top < window.innerHeight;

    if (!isAlreadyVisible) {
      el.classList.add('reveal-on-scroll');
      revealObserver.observe(el);
    }
  });
}

// 🛡️ Sentinel: Security Enhancement - Prevent Reverse Tabnabbing
// Automatically add rel="noopener noreferrer" to any external links that open in a new tab.
// This provides defense-in-depth against future content updates that might miss this attribute.
document.querySelectorAll('a[target="_blank"]:not([rel~="noopener"])').forEach(link => {
  link.rel = (link.rel + ' noopener noreferrer').trim();
});

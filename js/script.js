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

window.addEventListener('scroll', () => {
  const offset = 120; // Header height + buffer
  let activeLink = null;

  // Find the last section that has been passed
  navTargets.forEach(item => {
    if (window.scrollY >= item.target.offsetTop - offset) {
      activeLink = item.link;
    }
  });

  // Apply active class
  navLinks.forEach(link => {
    if (link === activeLink) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    } else {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    }
  });
});

// Back to Top Button Logic
const backToTopBtn = document.getElementById('back-to-top');

if (backToTopBtn) {
  window.addEventListener('scroll', () => {
    // Show button when scrolled down 500px
    if (window.scrollY > 500) {
      backToTopBtn.classList.add('visible');
    } else {
      backToTopBtn.classList.remove('visible');
    }
  });

  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

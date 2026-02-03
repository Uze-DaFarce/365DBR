// Simple success overlay for forms
document.querySelectorAll('a[href*="docs.google.com"]').forEach(a => {
  a.addEventListener('click', () => {
    const o = document.createElement('div');
    o.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(64,27,81,0.95);color:white;z-index:9999;display:flex;align-items:center;justify-content:center;font-size:18px;text-align:center;padding:20px;';
    o.innerHTML = '<div><div style="font-size:40px;margin-bottom:12px;">🙏</div>Thank you! We will review your message and reply soon.<br>Typically next business day.</div>';
    o.onclick = () => o.remove();
    document.body.appendChild(o);
    setTimeout(() => o.remove(), 8000);
  });
});

document.getElementById('copyright').innerHTML = `© 2024-${new Date().getFullYear()} Mt. Sinai LLC. All rights reserved. | Serving God through excellence in business.`;

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

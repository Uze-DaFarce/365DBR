(function () {
  'use strict';

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('./sw.js').catch(function () {});
    });
  }

  var DISMISS_KEY = 'hir_viewport_banner_dismissed';

  function isDismissed() {
    try {
      return sessionStorage.getItem(DISMISS_KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function shouldShowBanner() {
    return !isDismissed() && (window.innerWidth < 1000);
  }

  function syncBanner() {
    var existing = document.getElementById('hir-viewport-banner');
    if (!shouldShowBanner()) {
      if (existing) existing.remove();
      return;
    }
    if (existing) return;

    var bar = document.createElement('div');
    bar.id = 'hir-viewport-banner';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Edition switcher');
    bar.style.cssText = [
      'position:fixed',
      'top:0',
      'left:0',
      'right:0',
      'z-index:99999',
      'display:flex',
      'align-items:center',
      'justify-content:center',
      'gap:10px',
      'padding:8px 12px',
      'background:rgba(15,23,42,0.95)',
      'color:#f8fafc',
      'font-family:system-ui,-apple-system,sans-serif',
      'font-size:13px',
      'border-bottom:1px solid rgba(251,191,36,0.45)',
      'box-shadow:0 2px 8px rgba(0,0,0,0.4)'
    ].join(';');

    var text = document.createElement('span');
    text.textContent = 'Viewing on a smaller screen? Switch to the Mobile edition.';

    var link = document.createElement('a');
    link.href = '/m/';
    link.textContent = 'Open Mobile';
    link.style.cssText = 'padding:4px 10px;border-radius:6px;background:#f59e0b;color:#0f172a;font-weight:700;text-decoration:none;white-space:nowrap;';

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Dismiss banner');
    closeBtn.textContent = '\u00D7';
    closeBtn.style.cssText = 'margin-left:4px;background:transparent;border:none;color:#cbd5e1;font-size:18px;line-height:1;cursor:pointer;padding:2px 6px;';
    closeBtn.addEventListener('click', function () {
      try {
        sessionStorage.setItem(DISMISS_KEY, '1');
      } catch (e) {}
      bar.remove();
    });

    bar.appendChild(text);
    bar.appendChild(link);
    bar.appendChild(closeBtn);
    document.body.appendChild(bar);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncBanner);
  } else {
    syncBanner();
  }
  window.addEventListener('resize', syncBanner);
})();

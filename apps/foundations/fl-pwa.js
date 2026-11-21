if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/foundations/sw.js', { scope: '/foundations/' });
  });
}

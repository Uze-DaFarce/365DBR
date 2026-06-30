document.addEventListener("DOMContentLoaded", () => {
    goToPage(1);

    const btnEnter = document.getElementById('btn-enter');
    if (btnEnter) {
        btnEnter.addEventListener('click', (e) => {
            e.preventDefault();
            goToPage(4);
        });
    }

    // General nav to home for any nav with class or id containing nav-home
    const navHomes = document.querySelectorAll('[id*="nav-home"], .nav-home');
    navHomes.forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            goToPage(1);
        });
    });
});

function goToPage(pageNum) {
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    const target = document.getElementById(`page-${pageNum}`);
    if (target) {
        target.classList.add('active');
    }
}

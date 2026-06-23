document.addEventListener("DOMContentLoaded", () => {
    goToPage(1);

    const btnEnter = document.getElementById('btn-enter');
    if (btnEnter) {
        btnEnter.addEventListener('click', (e) => {
            e.preventDefault();
            goToPage(2);
        });
    }

    const navHomes = document.querySelectorAll('.nav-home, #nav-home');
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

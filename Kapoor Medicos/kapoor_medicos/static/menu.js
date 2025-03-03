document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".nav");

    menuToggle.addEventListener("click", function (event) {
        nav.classList.toggle("active");
        event.stopPropagation(); // Prevents the click from closing immediately
    });

    // Click outside to close menu
    document.addEventListener("click", function (event) {
        if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
            nav.classList.remove("active");
        }
    });
});



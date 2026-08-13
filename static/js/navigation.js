/* ============================================================
   ORIENTIQ — NAVIGATION
   ============================================================ */

(function () {
    "use strict";

    var navbar = document.querySelector(".navbar");
    var navbarToggle = document.querySelector(".navbar-toggle");
    var mobileMenu = document.querySelector(".mobile-menu");
    var mobileMenuClose = document.querySelector(".mobile-menu-close");
    var desktopDropdowns = document.querySelectorAll(".nav-item.has-dropdown");
    var mobileItems = document.querySelectorAll(".mobile-nav-item");

    /* ---------- Scroll state ---------- */
    function onScroll() {
        if (!navbar) return;
        if (window.scrollY > 10) {
            navbar.classList.add("is-scrolled");
        } else {
            navbar.classList.remove("is-scrolled");
        }
    }

    /* ---------- Desktop dropdowns (click + keyboard) ---------- */
    function closeAllDropdowns(except) {
        desktopDropdowns.forEach(function (item) {
            if (item !== except) {
                item.classList.remove("is-open");
                item.setAttribute("aria-expanded", "false");
            }
        });
    }

    function toggleDropdown(item) {
        var isOpen = item.classList.toggle("is-open");
        item.setAttribute("aria-expanded", isOpen ? "true" : "false");
        if (isOpen) {
            closeAllDropdowns(item);
        }
    }

    desktopDropdowns.forEach(function (item) {
        var trigger = item.querySelector(".nav-link");
        if (!trigger) return;

        trigger.addEventListener("click", function (e) {
            e.preventDefault();
            toggleDropdown(item);
        });

        // Close on Escape
        item.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                item.classList.remove("is-open");
                item.setAttribute("aria-expanded", "false");
                trigger.focus();
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener("click", function (e) {
        var isInside = false;
        desktopDropdowns.forEach(function (item) {
            if (item.contains(e.target)) {
                isInside = true;
            }
        });
        if (!isInside) {
            closeAllDropdowns();
        }
    });

    /* ---------- Mobile menu ---------- */
    function openMobileMenu() {
        if (!mobileMenu) return;
        mobileMenu.classList.add("is-open");
        mobileMenu.setAttribute("aria-hidden", "false");
        if (navbarToggle) {
            navbarToggle.setAttribute("aria-expanded", "true");
        }
        document.body.style.overflow = "hidden";
        if (mobileMenuClose) mobileMenuClose.focus();
    }

    function closeMobileMenu() {
        if (!mobileMenu) return;
        mobileMenu.classList.remove("is-open");
        mobileMenu.setAttribute("aria-hidden", "true");
        if (navbarToggle) {
            navbarToggle.setAttribute("aria-expanded", "false");
        }
        document.body.style.overflow = "";
        if (navbarToggle) navbarToggle.focus();
    }

    if (navbarToggle) {
        navbarToggle.addEventListener("click", openMobileMenu);
    }

    if (mobileMenuClose) {
        mobileMenuClose.addEventListener("click", closeMobileMenu);
    }

    // Close mobile menu on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeAllDropdowns();
            closeMobileMenu();
        }
    });

    // Close mobile menu when resizing to desktop
    window.addEventListener("resize", function () {
        if (window.innerWidth > 1024) {
            closeMobileMenu();
        }
    });

    /* ---------- Mobile submenu toggle ---------- */
    mobileItems.forEach(function (item) {
        var trigger = item.querySelector(".mobile-nav-link");
        if (!trigger) return;
        trigger.addEventListener("click", function (e) {
            e.preventDefault();
            var isOpen = item.classList.toggle("is-open");
            trigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    });

    /* ---------- Init ---------- */
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
})();
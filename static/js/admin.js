/* ============================================================
   ORIENTIQ — ADMIN DASHBOARD
   ============================================================ */

(function () {
    "use strict";

    var sidebar = document.getElementById("admin-sidebar");
    var sidebarToggle = document.querySelector(".admin-sidebar-toggle");
    var sidebarClose = document.querySelector(".admin-sidebar-close");

    function openSidebar() {
        if (sidebar) sidebar.classList.add("is-open");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("is-open");
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", openSidebar);
    }

    if (sidebarClose) {
        sidebarClose.addEventListener("click", closeSidebar);
    }

    // Close sidebar on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeSidebar();
        }
    });

    // Close sidebar when resizing to desktop
    window.addEventListener("resize", function () {
        if (window.innerWidth > 1024) {
            closeSidebar();
        }
    });
})();
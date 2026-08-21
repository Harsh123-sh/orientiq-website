/* AI & Automation page-only interaction layer. */
(function () {
    "use strict";

    document.querySelectorAll(".ai-faq-toggle").forEach(function (toggle) {
        toggle.addEventListener("click", function () {
            var item = toggle.closest(".ai-faq-item");
            var isOpen = item.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", String(isOpen));
        });
    });

    var visual = document.querySelector(".service-ai-page .service-detail-visual");
    if (!visual || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    visual.addEventListener("pointermove", function (event) {
        var bounds = visual.getBoundingClientRect();
        var x = (event.clientX - bounds.left) / bounds.width - 0.5;
        var y = (event.clientY - bounds.top) / bounds.height - 0.5;
        visual.style.setProperty("--ai-pointer-x", (x * 5).toFixed(2) + "px");
        visual.style.setProperty("--ai-pointer-y", (y * 5).toFixed(2) + "px");
    });

    visual.addEventListener("pointerleave", function () {
        visual.style.setProperty("--ai-pointer-x", "0px");
        visual.style.setProperty("--ai-pointer-y", "0px");
    });
})();

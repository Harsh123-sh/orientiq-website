(function () {
    "use strict";
    var modal = document.querySelector("[data-application-modal]");
    if (!modal) return;
    var dialog = modal.querySelector(".career-modal__dialog");
    var openers = document.querySelectorAll("[data-application-open]");
    var closers = modal.querySelectorAll("[data-application-close]");
    var activeTrigger = null;
    var scrollY = 0;

    // The page-enter animation transforms .site-main. Fixed descendants of a
    // transformed element are positioned against that element, not the viewport.
    // Move this existing dialog to body so it always uses the visual viewport.
    document.body.appendChild(modal);

    function closeModal() {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("career-modal-open");
        document.body.style.top = "";
        window.scrollTo(0, scrollY);
        if (activeTrigger) activeTrigger.focus();
    }
    function openModal(trigger) {
        activeTrigger = trigger;
        scrollY = window.scrollY;
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("career-modal-open");
        document.body.style.top = "-" + scrollY + "px";
        window.setTimeout(function () { (modal.querySelector("input, select, textarea, button") || dialog).focus(); }, 20);
    }
    openers.forEach(function (button) { button.addEventListener("click", function () { openModal(button); }); });
    closers.forEach(function (button) { button.addEventListener("click", closeModal); });
    document.addEventListener("keydown", function (event) { if (event.key === "Escape" && modal.classList.contains("is-open")) closeModal(); });
    if (modal.classList.contains("is-open")) {
        scrollY = window.scrollY;
        document.body.classList.add("career-modal-open");
        document.body.style.top = "-" + scrollY + "px";
    }
}());

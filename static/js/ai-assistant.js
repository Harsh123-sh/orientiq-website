/* ============================================================
   ORIENTIQ — AI ASSISTANT
   ============================================================ */

(function () {
    "use strict";

    var assistant = document.getElementById("ai-assistant");
    if (!assistant) return;

    var trigger = document.getElementById("ai-assistant-trigger");
    var panel = document.getElementById("ai-assistant-panel");
    var closeBtn = document.getElementById("ai-assistant-close");
    var clearBtn = document.getElementById("ai-assistant-clear");
    var messagesEl = document.getElementById("ai-assistant-messages");
    var errorEl = document.getElementById("ai-assistant-error");
    var form = document.getElementById("ai-assistant-form");
    var input = document.getElementById("ai-assistant-input");
    var sendBtn = document.getElementById("ai-assistant-send");
    var suggestionsEl = document.getElementById("ai-suggestions");
    var endpoint = assistant.getAttribute("data-endpoint");

    var conversationHistory = [];

    /* ---------- Open / Close ---------- */
    function openAssistant() {
        panel.classList.add("is-open");
        panel.setAttribute("aria-hidden", "false");
        trigger.setAttribute("aria-expanded", "true");
        if (input) input.focus();
    }

    function closeAssistant() {
        panel.classList.remove("is-open");
        panel.setAttribute("aria-hidden", "true");
        trigger.setAttribute("aria-expanded", "false");
        trigger.focus();
    }

    if (trigger) {
        trigger.addEventListener("click", function () {
            if (panel && panel.classList.contains("is-open")) {
                closeAssistant();
            } else {
                openAssistant();
            }
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeAssistant);
    }

    // Close on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && panel && panel.classList.contains("is-open")) {
            closeAssistant();
        }
    });

    /* ---------- Messages ---------- */
    function addMessage(role, text) {
        var wrapper = document.createElement("div");
        wrapper.className = "ai-message ai-message-" + role;
        wrapper.setAttribute("data-role", role);

        var bubble = document.createElement("div");
        bubble.className = "ai-message-bubble";
        bubble.textContent = text; // safe: textContent escapes HTML
        wrapper.appendChild(bubble);

        messagesEl.appendChild(wrapper);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return wrapper;
    }

    function addTypingIndicator() {
        var wrapper = document.createElement("div");
        wrapper.className = "ai-message ai-message-assistant ai-typing";
        wrapper.setAttribute("aria-label", "Orientiq AI is typing");

        var bubble = document.createElement("div");
        bubble.className = "ai-message-bubble";
        for (var i = 0; i < 3; i++) {
            var dot = document.createElement("span");
            dot.className = "ai-typing-dot";
            bubble.appendChild(dot);
        }
        wrapper.appendChild(bubble);
        messagesEl.appendChild(wrapper);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return wrapper;
    }

    function addCtaSuggestions(suggestions) {
        var ctaWrap = document.createElement("div");
        ctaWrap.className = "ai-cta-suggestions";

        suggestions.forEach(function (s) {
            var link = document.createElement("a");
            link.className = "ai-cta-link";
            link.href = s.url;
            link.textContent = "→ " + s.label;
            ctaWrap.appendChild(link);
        });

        messagesEl.appendChild(ctaWrap);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    /* ---------- Clear conversation ---------- */
    function clearConversation() {
        if (!messagesEl) return;

        // Remove all message/CTA elements except the initial greeting block.
        var children = messagesEl.querySelectorAll(
            ".ai-message, .ai-cta-suggestions, .ai-suggestion-label, .ai-suggestions"
        );
        children.forEach(function (child) {
            // Keep the initial greeting message.
            if (child.querySelector && child.querySelector("[data-role]") && child.hasAttribute("data-role")) {
                // already has role; leave it
            }
            child.remove();
        });

        // Reset to the initial greeting state if the messages container is empty.
        if (messagesEl.querySelectorAll(".ai-message").length === 0) {
            var greeting = document.createElement("div");
            greeting.className = "ai-message ai-message-assistant";
            greeting.setAttribute("data-role", "assistant");
            var bubble = document.createElement("div");
            bubble.className = "ai-message-bubble";
            bubble.textContent = "Hello! I'm Orientiq AI. How can I help you today?";
            greeting.appendChild(bubble);
            messagesEl.appendChild(greeting);
        }

        // Re-add suggestion options.
        var label = document.createElement("p");
        label.className = "ai-suggestion-label";
        label.textContent = "Try asking:";
        messagesEl.appendChild(label);

        var sugWrap = document.createElement("div");
        sugWrap.className = "ai-suggestions";
        var questions = [
            "What does Orientiq do?",
            "What services do you provide?",
            "Which industries do you serve?",
            "What technologies do you use?",
            "Tell me about your products.",
            "How can I start a project?"
        ];
        questions.forEach(function (q) {
            var chip = document.createElement("button");
            chip.type = "button";
            chip.className = "ai-suggestion-chip";
            chip.setAttribute("data-question", q);
            chip.textContent = q;
            chip.addEventListener("click", function () {
                sendMessage(q);
            });
            sugWrap.appendChild(chip);
        });
        messagesEl.appendChild(sugWrap);

        conversationHistory = [];
        hideError();
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", clearConversation);
    }

    /* ---------- Error ---------- */
    function showError() {
        if (errorEl) errorEl.hidden = false;
    }

    function hideError() {
        if (errorEl) errorEl.hidden = true;
    }

    /* ---------- Send ---------- */
    function sendMessage(message) {
        message = (message || "").trim();
        if (!message) return;

        hideError();

        // Add user message.
        addMessage("user", message);

        // Add typing indicator.
        var typing = addTypingIndicator();

        // Disable send while waiting.
        if (sendBtn) sendBtn.disabled = true;
        if (input) input.disabled = true;

        // Push user message to history.
        conversationHistory.push({ user: message, assistant: "" });

        var body = JSON.stringify({
            message: message,
            history: conversationHistory.slice(0, 10)
        });

        fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: body
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                typing.remove();

                if (!result.ok || !result.data.success) {
                    showError();
                    // Still record an assistant error message in history as empty.
                    if (conversationHistory.length) {
                        conversationHistory[conversationHistory.length - 1].assistant =
                            "I'm having trouble connecting right now. Please try again in a moment.";
                    }
                    return;
                }

                var text = result.data.message || "";
                addMessage("assistant", text);

                // Update history.
                if (conversationHistory.length) {
                    conversationHistory[conversationHistory.length - 1].assistant = text;
                }

                // Add CTA suggestions.
                var suggestions = result.data.suggestions || [];
                if (suggestions.length) {
                    addCtaSuggestions(suggestions);
                }
            })
            .catch(function () {
                typing.remove();
                showError();
                if (conversationHistory.length) {
                    conversationHistory[conversationHistory.length - 1].assistant = "";
                }
            })
            .finally(function () {
                if (sendBtn) sendBtn.disabled = false;
                if (input) input.disabled = false;
                if (input) input.focus();
            });
    }

    /* ---------- Form submit ---------- */
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var message = input ? input.value : "";
            if (message.trim()) {
                sendMessage(message);
                input.value = "";
                input.style.height = "auto";
            }
        });
    }

    // Enter to send; Shift+Enter for newline.
    if (input) {
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (form) form.dispatchEvent(new Event("submit", { cancelable: true }));
            }
        });

        // Auto-grow the textarea.
        input.addEventListener("input", function () {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 120) + "px";
        });
    }

    /* ---------- Suggestion chips ---------- */
    if (suggestionsEl) {
        suggestionsEl.addEventListener("click", function (e) {
            var chip = e.target.closest(".ai-suggestion-chip");
            if (chip) {
                sendMessage(chip.getAttribute("data-question"));
            }
        });
    }

    /* ---------- CSRF token helper ---------- */
    function getCookie(name) {
        var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        if (match) return decodeURIComponent(match[2]);
        return "";
    }
})();
/* ============================================================
   ORENTIQ — AI ASSISTANT
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
    var endpoint = assistant.getAttribute("data-endpoint");
    var inquiryEndpoint = assistant.getAttribute("data-inquiry-endpoint");
    var robotImage = assistant.getAttribute("data-robot-image");

    var conversationHistory = [];
    var suggestedQuestions = [
        {
            question: "What does ORENTIQ do?",
            icon: "M4 10 12 4l8 6v10H4zM9 20v-6h6v6M8 10h.01M16 10h.01"
        },
        {
            question: "Who is the founder?",
            icon: "M12 8a4 4 0 1 0 0-8 4 4 0 0 0 0 8M4 21a8 8 0 0 1 16 0"
        },
        {
            question: "What services do you provide?",
            icon: "M5 7h14v12H5zM8 11h8M8 15h5M8 4h8"
        },
        {
            question: "Which industries do you serve?",
            icon: "M3 20V9l6 3V8l6 4V4h6v16zM17 8h1M17 11h1M7 16h1M12 16h1"
        },
        {
            question: "I want to start a project.",
            icon: "M12 3v18M3 12h18M5 5l14 14M19 5 5 19"
        }
    ];

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
            wrapper.setAttribute("aria-label", "ORENTIQ AI is typing");

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

    function createWelcomeMessage() {
        var greeting = document.createElement("div");
        greeting.className = "ai-message ai-message-assistant";
        greeting.setAttribute("data-role", "assistant");

        var avatar = document.createElement("span");
        avatar.className = "ai-message-avatar";
        avatar.setAttribute("aria-hidden", "true");
        var image = document.createElement("img");
        image.src = robotImage;
        image.alt = "";
        avatar.appendChild(image);
        greeting.appendChild(avatar);

        var bubble = document.createElement("div");
        bubble.className = "ai-message-bubble ai-welcome-bubble";
        var title = document.createElement("strong");
        title.className = "ai-welcome-title";
        title.textContent = "Hello! I'm ORENTIQ AI.";
        var copy = document.createElement("span");
        copy.className = "ai-welcome-copy";
        copy.textContent = "May I help you? I'm here to guide you through ORENTIQ's services and solutions.";
        bubble.appendChild(title);
        bubble.appendChild(copy);
        greeting.appendChild(bubble);
        return greeting;
    }

    function createSuggestion(question) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "ai-suggestion-chip";
        chip.setAttribute("data-question", question.question);

        var icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        icon.setAttribute("class", "ai-suggestion-icon");
        icon.setAttribute("viewBox", "0 0 24 24");
        icon.setAttribute("aria-hidden", "true");
        var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", question.icon);
        icon.appendChild(path);

        var text = document.createElement("span");
        text.textContent = question.question;
        var chevron = document.createElement("span");
        chevron.className = "ai-suggestion-chevron";
        chevron.setAttribute("aria-hidden", "true");
        chevron.textContent = "›";
        chip.appendChild(icon);
        chip.appendChild(text);
        chip.appendChild(chevron);
        return chip;
    }

    function createSubmissionId() {
        if (window.crypto && typeof window.crypto.randomUUID === "function") {
            return window.crypto.randomUUID();
        }
        if (window.crypto && typeof window.crypto.getRandomValues === "function") {
            var bytes = new Uint8Array(16);
            window.crypto.getRandomValues(bytes);
            bytes[6] = (bytes[6] & 15) | 64;
            bytes[8] = (bytes[8] & 63) | 128;
            var hex = Array.prototype.map.call(bytes, function (byte) {
                return byte.toString(16).padStart(2, "0");
            }).join("");
            return hex.slice(0, 8) + "-" + hex.slice(8, 12) + "-" +
                hex.slice(12, 16) + "-" + hex.slice(16, 20) + "-" + hex.slice(20);
        }
        throw new Error("Secure inquiry submission IDs are not supported by this browser.");
    }

    function addInquiryForm() {
        var template = document.getElementById("ai-inquiry-form-template");
        if (!template || !template.content.firstElementChild) {
            showError();
            return;
        }

        var wrapper = document.createElement("div");
        wrapper.className = "ai-inquiry-card";
        var formElement = template.content.firstElementChild.cloneNode(true);
        formElement.querySelector('[name="submission_id"]').value = createSubmissionId();
        wrapper.appendChild(formElement);
        messagesEl.appendChild(wrapper);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function submitInquiry(formElement) {
        var submitButton = formElement.querySelector(".ai-inquiry-submit");
        var errorElement = formElement.querySelector(".ai-inquiry-form-error");
        var fieldErrors = formElement.querySelectorAll(".ai-inquiry-field-error");
        fieldErrors.forEach(function (error) { error.remove(); });
        errorElement.hidden = true;
        submitButton.disabled = true;

        fetch(inquiryEndpoint, {
            method: "POST",
            headers: { "X-CSRFToken": getCsrfToken() },
            body: new FormData(formElement)
        })
            .then(function (response) {
                var contentType = response.headers.get("content-type") || "";
                if (!contentType.includes("application/json")) {
                    throw new Error("The server rejected the inquiry (HTTP " + response.status + "). Please refresh and try again.");
                }
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data, status: response.status };
                });
            })
            .then(function (result) {
                if (!result.ok || !result.data.success) {
                    if (result.data.errors) {
                        Object.keys(result.data.errors).forEach(function (name) {
                            var field = formElement.elements.namedItem(name);
                            var errors = result.data.errors[name];
                            if (!field || !errors.length) return;
                            var message = document.createElement("span");
                            message.className = "ai-inquiry-field-error";
                            message.textContent = errors.map(function (error) { return error.message; }).join(" ");
                            field.insertAdjacentElement("afterend", message);
                        });
                    }
                    errorElement.textContent = result.data.message ||
                        "The inquiry could not be submitted (HTTP " + result.status + "). Please try again.";
                    errorElement.hidden = false;
                    return;
                }

                var success = document.createElement("div");
                success.className = "ai-inquiry-success";
                success.setAttribute("role", "status");
                success.textContent = result.data.message + " Your reference is " + result.data.reference + ".";
                formElement.closest(".ai-inquiry-card").replaceWith(success);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            })
            .catch(function (error) {
                errorElement.textContent = error.message || "The inquiry could not be submitted. Please try again.";
                errorElement.hidden = false;
            })
            .finally(function () {
                submitButton.disabled = false;
            });
    }

    /* ---------- Clear conversation ---------- */
    function clearConversation() {
        if (!messagesEl) return;

        messagesEl.replaceChildren(createWelcomeMessage());
        var label = document.createElement("p");
        label.className = "ai-suggestion-label";
        label.textContent = "Try asking";
        messagesEl.appendChild(label);

        var sugWrap = document.createElement("div");
        sugWrap.className = "ai-suggestions";
        sugWrap.id = "ai-suggestions";
        suggestedQuestions.forEach(function (question) {
            sugWrap.appendChild(createSuggestion(question));
        });
        messagesEl.appendChild(sugWrap);

        conversationHistory = [];
        hideError();
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", clearConversation);
    }

    /* ---------- Error ---------- */
    function showError(message) {
        if (errorEl) {
            errorEl.textContent = message || "I'm having trouble connecting right now. Please try again in a moment.";
            errorEl.hidden = false;
        }
    }

    function hideError() {
        if (errorEl) errorEl.hidden = true;
    }

    /* ---------- Send ---------- */
    function sendMessage(message) {
        message = (message || "").trim();
        if (!message) return;

        hideError();
        var suggestionLabel = messagesEl.querySelector(".ai-suggestion-label");
        var suggestions = messagesEl.querySelector(".ai-suggestions");
        if (suggestionLabel) suggestionLabel.remove();
        if (suggestions) suggestions.remove();

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
                "X-CSRFToken": getCsrfToken()
            },
            body: body
        })
            .then(function (response) {
                return response.text().then(function (text) {
                    var data;
                    try {
                        data = JSON.parse(text);
                    } catch (error) {
                        if (!response.ok) {
                            throw new Error("The chat request was rejected (HTTP " + response.status + ").");
                        }
                        throw new Error("The chat server returned an invalid response.");
                    }
                    return { ok: response.ok, data: data, status: response.status };
                });
            })
            .then(function (result) {
                typing.remove();

                if (!result.ok || !result.data.success) {
                    showError((result.data.message || "The chat request could not be completed.") +
                        " (HTTP " + result.status + ")");
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
                if (result.data.show_inquiry_form) {
                    addInquiryForm();
                }
            })
            .catch(function (error) {
                typing.remove();
                showError(error.message);
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
    if (messagesEl) {
        messagesEl.addEventListener("click", function (e) {
            var chip = e.target.closest(".ai-suggestion-chip");
            if (chip) {
                sendMessage(chip.getAttribute("data-question"));
            }
        });
        messagesEl.addEventListener("submit", function (e) {
            if (e.target.matches(".ai-inquiry-form")) {
                e.preventDefault();
                submitInquiry(e.target);
            }
        });
    }

    /* ---------- CSRF token helper ---------- */
    function getCookie(name) {
        var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        if (match) return decodeURIComponent(match[2]);
        return "";
    }

    function getCsrfToken() {
        var tokenInput = form && form.querySelector('input[name="csrfmiddlewaretoken"]');
        return tokenInput ? tokenInput.value : getCookie("csrftoken");
    }
})();
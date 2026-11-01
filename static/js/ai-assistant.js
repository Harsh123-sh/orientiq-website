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
    var businessEndpoint = assistant.getAttribute("data-business-endpoint");
    var consultationAvailabilityEndpoint = assistant.getAttribute("data-consultation-availability-endpoint");
    var consultationEndpoint = assistant.getAttribute("data-consultation-endpoint");
    var supportEndpoint = assistant.getAttribute("data-support-endpoint");
    var robotImage = assistant.getAttribute("data-robot-image");

    var conversationHistory = [];
    var conversationReference = "";
    var newConversation = false;
    var pendingTurn = null;
    var pendingSubmission = null;
    var knowledgeModeDisclosed = false;
    var businessInfoLoaded = false;
    var speechRecognition = null;
    var speechEnabled = false;
    var knownContactDetails = {};
    var conversationConsent = document.getElementById("ai-conversation-consent");
    var languageSelect = document.getElementById("ai-language");
    var voiceButton = document.getElementById("ai-voice-input");
    var voiceStatus = document.getElementById("ai-voice-status");
    var speechToggle = document.getElementById("ai-speech-toggle");
    var deleteDataButton = document.getElementById("ai-delete-data");
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
        loadBusinessInfo();
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
        appendSafeLinkedText(bubble, text);
        wrapper.appendChild(bubble);

        messagesEl.appendChild(wrapper);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return wrapper;
    }

    function addKnowledgeModeNotice() {
        if (knowledgeModeDisclosed) return;
        var notice = document.createElement("p");
        notice.className = "ai-mode-notice";
        notice.textContent = "Website knowledge mode: answers are limited to verified ORENTIQ information.";
        messagesEl.appendChild(notice);
        knowledgeModeDisclosed = true;
    }

    function safeHref(value) {
        if (/^\/(?!\/)[A-Za-z0-9/_-]*\/?$/.test(value)) return value;
        if (/^(?:mailto:)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/i.test(value)) return value;
        if (/^tel:\+?[0-9]{7,15}$/.test(value)) return value;
        try {
            var url = new URL(value);
            if (url.protocol === "https:" &&
                ["orentiq.me", "www.orentiq.me", "orentiq.com", "www.orentiq.com", "wa.me"].includes(url.hostname)) {
                return url.href;
            }
        } catch (error) {
            return "";
        }
        return "";
    }

    function appendSafeLinkedText(element, text) {
        var linkPattern = /(https:\/\/[^\s]+|mailto:[^\s]+|tel:\+?[0-9]{7,15}|\/[A-Za-z0-9/_-]*\/?)/gi;
        var cursor = 0;
        var match;
        var content = String(text || "");
        while ((match = linkPattern.exec(content)) !== null) {
            if (match.index > cursor) {
                element.appendChild(document.createTextNode(content.slice(cursor, match.index)));
            }
            var raw = match[0];
            var trailing = "";
            while (/[.,;!?)]$/.test(raw)) {
                trailing = raw.slice(-1) + trailing;
                raw = raw.slice(0, -1);
            }
            var href = safeHref(raw);
            if (href && raw) {
                var link = document.createElement("a");
                link.href = href;
                link.textContent = raw;
                if (/^https:/.test(href)) {
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                }
                element.appendChild(link);
            } else {
                element.appendChild(document.createTextNode(raw));
            }
            if (trailing) element.appendChild(document.createTextNode(trailing));
            cursor = match.index + match[0].length;
        }
        if (cursor < content.length) {
            element.appendChild(document.createTextNode(content.slice(cursor)));
        }
        var emailPattern = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
        var childNodes = Array.prototype.slice.call(element.childNodes);
        childNodes.forEach(function (node) {
            if (node.nodeType !== Node.TEXT_NODE) return;
            var value = node.textContent;
            var emailMatch;
            var last = 0;
            var fragment = document.createDocumentFragment();
            var hasEmail = false;
            while ((emailMatch = emailPattern.exec(value)) !== null) {
                hasEmail = true;
                if (emailMatch.index > last) {
                    fragment.appendChild(document.createTextNode(value.slice(last, emailMatch.index)));
                }
                var emailLink = document.createElement("a");
                emailLink.href = "mailto:" + emailMatch[0];
                emailLink.textContent = emailMatch[0];
                fragment.appendChild(emailLink);
                last = emailMatch.index + emailMatch[0].length;
            }
            if (hasEmail) {
                if (last < value.length) fragment.appendChild(document.createTextNode(value.slice(last)));
                node.replaceWith(fragment);
            }
            emailPattern.lastIndex = 0;
        });
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
            var href = safeHref(s.url);
            if (!href) return;
            var link = document.createElement("a");
            link.className = "ai-cta-link";
            link.href = href;
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

    var inquiryQuestions = [
        { key: "name", label: "What is your full name?", type: "text", required: true, maxLength: 120, autocomplete: "name" },
        { key: "email", label: "What is your business email?", type: "email", required: true, maxLength: 254, autocomplete: "email" },
        { key: "phone", label: "What phone or WhatsApp number can we use? (Optional)", type: "tel", maxLength: 30, autocomplete: "tel" },
        { key: "company", label: "What is your company name? (Optional)", type: "text", maxLength: 120, autocomplete: "organization" },
        {
            key: "inquiry_type",
            label: "Which service are you interested in?",
            type: "select",
            required: true,
            options: [
                ["", "Select a service"],
                ["website_development", "Website Development"],
                ["mobile_application", "Mobile Application"],
                ["custom_software", "Custom Software"],
                ["business_dashboard", "Business Dashboard"],
                ["ai_automation", "AI & Automation"],
                ["saas_product", "SaaS Product"],
                ["society_school_management", "Society or School Management"],
                ["other", "Other"]
            ]
        },
        { key: "title", label: "What would you like to call this project?", type: "text", required: true, maxLength: 160 },
        { key: "description", label: "Tell us a little about the project and what you need.", type: "textarea", required: true, maxLength: 5000 },
        { key: "budget", label: "Do you have a budget range in mind? (Optional)", type: "text", maxLength: 80 },
        { key: "timeline", label: "When would you like to begin or launch? (Optional)", type: "text", maxLength: 80 },
        {
            key: "contact_method",
            label: "How would you prefer we contact you? (Optional)",
            type: "select",
            options: [["", "No preference"], ["email", "Email"], ["phone", "Phone"], ["whatsapp", "WhatsApp"]]
        }
    ];

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
        formElement.querySelector('[name="conversation_reference"]').value = conversationReference || createSubmissionId();
        formElement.querySelector('[name="language"]').value = getSelectedLanguage();
        wrapper.appendChild(formElement);
        messagesEl.appendChild(wrapper);
        formElement._inquiryStep = 0;
        formElement._editingStep = false;
        formElement.querySelector(".ai-inquiry-privacy-continue").addEventListener("click", function () {
            var consent = formElement.elements.namedItem("collection_consent");
            if (!consent.checked) {
                consent.reportValidity();
                return;
            }
            formElement.querySelector(".ai-inquiry-privacy-step").hidden = true;
            formElement.querySelector(".ai-inquiry-step").hidden = false;
            renderInquiryQuestion(formElement, 0, false);
        });
        formElement.querySelector(".ai-inquiry-next").addEventListener("click", function () {
            advanceInquiry(formElement, false);
        });
        formElement.querySelector(".ai-inquiry-skip").addEventListener("click", function () {
            advanceInquiry(formElement, true);
        });
        formElement.querySelector(".ai-inquiry-confirm").addEventListener("click", function () {
            formElement.querySelector(".ai-inquiry-review").hidden = true;
            formElement.querySelector(".ai-inquiry-confirmation").hidden = false;
            formElement.querySelector('[name="consent"]').focus();
        });
        formElement.querySelector(".ai-inquiry-back").addEventListener("click", function () {
            formElement.querySelector(".ai-inquiry-confirmation").hidden = true;
            formElement.querySelector(".ai-inquiry-review").hidden = false;
        });
        formElement.querySelector(".ai-inquiry-cancel").addEventListener("click", function () {
            pendingSubmission = null;
            wrapper.remove();
            addMessage("assistant", "No inquiry was submitted. You can start again whenever you're ready.");
        });
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function renderInquiryQuestion(formElement, index, editing) {
        var question = inquiryQuestions[index];
        var step = formElement.querySelector(".ai-inquiry-step");
        var label = step.querySelector(".ai-inquiry-question");
        var progress = step.querySelector(".ai-inquiry-progress");
        var next = step.querySelector(".ai-inquiry-next");
        var skip = step.querySelector(".ai-inquiry-skip");
        var control = document.createElement(question.type === "textarea" ? "textarea" : question.type === "select" ? "select" : "input");
        var nameInput = formElement.elements.namedItem(question.key);
        formElement._inquiryStep = index;
        formElement._editingStep = editing;
        progress.textContent = "Question " + (index + 1) + " of " + inquiryQuestions.length;
        label.replaceChildren();
        label.appendChild(document.createTextNode(question.label));
        if (question.required) {
            var requiredMark = document.createElement("span");
            requiredMark.textContent = " *";
            label.appendChild(requiredMark);
        }
        control.className = "ai-inquiry-control";
        control.setAttribute("aria-label", question.label);
        control.maxLength = question.maxLength || 200;
        control.required = Boolean(question.required);
        if (question.autocomplete) control.autocomplete = question.autocomplete;
        if (question.type === "select") {
            question.options.forEach(function (option) {
                var optionElement = document.createElement("option");
                optionElement.value = option[0];
                optionElement.textContent = option[1];
                control.appendChild(optionElement);
            });
        } else if (question.type === "textarea") {
            control.rows = 3;
        } else {
            control.type = question.type;
        }
        control.value = nameInput.value;
        label.appendChild(control);
        next.textContent = index === inquiryQuestions.length - 1 ? "Review answers" : "Continue";
        skip.hidden = Boolean(question.required);
        step.hidden = false;
        formElement.querySelector(".ai-inquiry-review").hidden = true;
        formElement.querySelector(".ai-inquiry-confirmation").hidden = true;
        control.focus();
    }

    function advanceInquiry(formElement, skip) {
        var question = inquiryQuestions[formElement._inquiryStep];
        var control = formElement.querySelector(".ai-inquiry-control");
        if (!skip) {
            if (!control.value.trim()) control.value = "";
            if (!control.checkValidity()) {
                control.reportValidity();
                return;
            }
            formElement.elements.namedItem(question.key).value = control.value.trim();
        } else {
            formElement.elements.namedItem(question.key).value = "";
        }

        pendingSubmission = null;
        var errorElement = formElement.querySelector(".ai-inquiry-form-error");
        errorElement.hidden = true;
        if (formElement._editingStep) {
            showInquiryReview(formElement);
            return;
        }
        var nextIndex = formElement._inquiryStep + 1;
        if (nextIndex < inquiryQuestions.length) {
            renderInquiryQuestion(formElement, nextIndex, false);
        } else {
            showInquiryReview(formElement);
        }
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showInquiryReview(formElement) {
        formElement.querySelector(".ai-inquiry-step").hidden = true;
        var review = formElement.querySelector(".ai-inquiry-review");
        var list = review.querySelector(".ai-inquiry-review-list");
        list.replaceChildren();
        inquiryQuestions.forEach(function (question, index) {
            var row = document.createElement("div");
            row.className = "ai-inquiry-review-row";
            var details = document.createElement("div");
            var label = document.createElement("strong");
            label.textContent = question.label.replace(/\s*\(Optional\)/, "").replace(/\?$/, "");
            var value = document.createElement("span");
            var savedValue = formElement.elements.namedItem(question.key).value;
            if (question.type === "select" && savedValue) {
                var selectedOption = question.options.find(function (option) { return option[0] === savedValue; });
                savedValue = selectedOption ? selectedOption[1] : savedValue;
            }
            value.textContent = savedValue || "Not provided";
            details.appendChild(label);
            details.appendChild(value);
            var edit = document.createElement("button");
            edit.type = "button";
            edit.className = "ai-inquiry-edit";
            edit.textContent = "Edit";
            edit.setAttribute("aria-label", "Edit " + question.label);
            edit.addEventListener("click", function () {
                renderInquiryQuestion(formElement, index, true);
            });
            row.appendChild(details);
            row.appendChild(edit);
            list.appendChild(row);
        });
        review.hidden = false;
        formElement.querySelector(".ai-inquiry-confirmation").hidden = true;
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function submitInquiry(formElement) {
        var submitButton = formElement.querySelector(".ai-inquiry-submit");
        var errorElement = formElement.querySelector(".ai-inquiry-form-error");
        var consent = formElement.elements.namedItem("consent");
        if (!consent.checked) {
            consent.reportValidity();
            return;
        }
        var attachmentInput = formElement.elements.namedItem("attachments");
        var selectedFiles = attachmentInput ? attachmentInput.files : [];
        if (selectedFiles.length > 5 || Array.from(selectedFiles).some(function (file) {
            return file.size > 10 * 1024 * 1024;
        })) {
            errorElement.textContent = "Choose no more than five files, each 10 MB or smaller.";
            errorElement.hidden = false;
            return;
        }
        if (!pendingSubmission || pendingSubmission.formElement !== formElement) {
            formElement.elements.namedItem("conversation_transcript").value = createTranscript();
            pendingSubmission = {
                formElement: formElement,
                body: new FormData(formElement)
            };
        }
        errorElement.replaceChildren();
        errorElement.hidden = true;
        submitButton.disabled = true;

        fetch(inquiryEndpoint, {
            method: "POST",
            headers: { "X-CSRFToken": getCsrfToken() },
            body: pendingSubmission.body
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
                    errorElement.textContent = result.data.message ||
                        "The inquiry could not be submitted (HTTP " + result.status + "). Please try again.";
                    errorElement.hidden = false;
                    if (result.status === 400) {
                        pendingSubmission = null;
                        addInquiryReviewAction(formElement, errorElement);
                    } else if (result.status !== 409) {
                        lockInquiryAfterFailure(formElement);
                        addInquiryRetry(formElement, errorElement);
                    } else {
                        lockInquiryAfterFailure(formElement);
                    }
                    return;
                }

                var success = document.createElement("div");
                knownContactDetails = {
                    name: formElement.elements.namedItem("name").value,
                    email: formElement.elements.namedItem("email").value,
                    phone: formElement.elements.namedItem("phone").value
                };
                success.className = "ai-inquiry-success";
                success.setAttribute("role", "status");
                success.textContent = result.data.message + " Your reference is " + result.data.reference + ".";
                formElement.closest(".ai-inquiry-card").replaceWith(success);
                pendingSubmission = null;
                messagesEl.scrollTop = messagesEl.scrollHeight;
            })
            .catch(function (error) {
                errorElement.textContent = error.message || "The inquiry could not be submitted. Please try again.";
                errorElement.hidden = false;
                lockInquiryAfterFailure(formElement);
                addInquiryRetry(formElement, errorElement);
            })
            .finally(function () {
                submitButton.disabled = false;
            });
    }

    function addInquiryRetry(formElement, errorElement) {
        var retry = document.createElement("button");
        retry.type = "button";
        retry.className = "ai-inquiry-retry";
        retry.textContent = "Retry submission";
        retry.addEventListener("click", function () {
            submitInquiry(formElement);
        });
        errorElement.appendChild(retry);
    }

    function lockInquiryAfterFailure(formElement) {
        formElement.querySelector(".ai-inquiry-back").hidden = true;
        formElement.elements.namedItem("consent").disabled = true;
    }

    function addInquiryReviewAction(formElement, errorElement) {
        var reviewButton = document.createElement("button");
        reviewButton.type = "button";
        reviewButton.className = "ai-inquiry-retry";
        reviewButton.textContent = "Review and correct details";
        reviewButton.addEventListener("click", function () {
            formElement.elements.namedItem("consent").disabled = false;
            formElement.querySelector(".ai-inquiry-confirmation").hidden = true;
            formElement.querySelector(".ai-inquiry-review").hidden = false;
            errorElement.hidden = true;
        });
        errorElement.appendChild(reviewButton);
    }

    function createTranscript() {
        var transcript = [];
        conversationHistory.forEach(function (turn) {
            if (turn.user) transcript.push({ role: "user", text: turn.user.slice(0, 1800) });
            if (turn.assistant) transcript.push({ role: "assistant", text: turn.assistant.slice(0, 1800) });
        });
        transcript = transcript.slice(-60);
        while (transcript.length && JSON.stringify(transcript).length > 9500) {
            transcript.shift();
        }
        return JSON.stringify(transcript);
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
        conversationReference = "";
        newConversation = true;
        knownContactDetails = {};
        pendingTurn = null;
        pendingSubmission = null;
        knowledgeModeDisclosed = false;
        if (conversationConsent) conversationConsent.checked = false;
        if ("speechSynthesis" in window) window.speechSynthesis.cancel();
        if (sendBtn) sendBtn.disabled = false;
        if (input) input.disabled = false;
        hideError();
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", clearConversation);
    }

    if (deleteDataButton) {
        deleteDataButton.addEventListener("click", function () {
            if (!window.confirm("Delete saved chatbot conversation data and linked chatbot inquiries for this browser session?")) return;
            deleteDataButton.disabled = true;
            fetch(assistant.getAttribute("data-delete-data-endpoint"), {
                method: "POST",
                headers: { "X-CSRFToken": getCsrfToken() }
            }).then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok || !data.success) throw new Error(data.message || "Data deletion could not be completed.");
                    clearConversation();
                    addMessage("assistant", data.message);
                });
            }).catch(function (error) {
                showError(error.message);
            }).finally(function () {
                deleteDataButton.disabled = false;
            });
        });
    }

    /* ---------- Error ---------- */
    function showError(message, onRetry) {
        if (errorEl) {
            errorEl.replaceChildren(document.createTextNode(
                message || "I'm having trouble connecting right now. Please try again in a moment."
            ));
            if (onRetry) {
                var retry = document.createElement("button");
                retry.type = "button";
                retry.className = "ai-chat-retry";
                retry.textContent = "Retry";
                retry.addEventListener("click", onRetry);
                errorEl.appendChild(retry);
            }
            errorEl.hidden = false;
        }
    }

    function hideError() {
        if (errorEl) {
            errorEl.hidden = true;
            errorEl.replaceChildren();
        }
    }

    /* ---------- Send ---------- */
    function sendMessage(message, retryTurn) {
        message = (message || "").trim();
        if (!message) return;
        if (pendingTurn && !retryTurn) return;

        hideError();
        var suggestionLabel = messagesEl.querySelector(".ai-suggestion-label");
        var suggestions = messagesEl.querySelector(".ai-suggestions");
        if (suggestionLabel) suggestionLabel.remove();
        if (suggestions) suggestions.remove();

        var turn = retryTurn;
        if (!turn) {
            addMessage("user", message);
            turn = { user: message, assistant: "" };
            conversationHistory.push(turn);
        } else {
            pendingTurn = null;
        }

        // Add typing indicator.
        var typing = addTypingIndicator();

        // Disable send while waiting.
        if (sendBtn) sendBtn.disabled = true;
        if (input) input.disabled = true;

        var body = JSON.stringify({
            message: message,
            history: conversationHistory.slice(-10),
            language: getSelectedLanguage(),
            conversation_consent: Boolean(conversationConsent && conversationConsent.checked),
            conversation_reference: conversationReference,
            new_conversation: newConversation
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
                    pendingTurn = turn;
                    showError((result.data.message || "The chat request could not be completed.") +
                        " (HTTP " + result.status + ")", function () {
                        sendMessage(message, turn);
                    });
                    return;
                }

                var text = result.data.message || "";
                conversationReference = result.data.conversation_reference || conversationReference;
                newConversation = false;
                if (result.data.mode === "knowledge") addKnowledgeModeNotice();
                addMessage("assistant", text);
                speakReply(text);

                // Update history.
                turn.assistant = text;
                pendingTurn = null;

                // Add CTA suggestions.
                var suggestions = result.data.suggestions || [];
                if (suggestions.length) {
                    addCtaSuggestions(suggestions);
                }
                if (result.data.start_inquiry) {
                    addInquiryForm();
                }
            })
            .catch(function (error) {
                typing.remove();
                pendingTurn = turn;
                showError(error.message, function () {
                    sendMessage(message, turn);
                });
            })
            .finally(function () {
                if (!pendingTurn) {
                    if (sendBtn) sendBtn.disabled = false;
                    if (input) input.disabled = false;
                    if (input) input.focus();
                }
            });
    }

    /* ---------- Form submit ---------- */
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (pendingTurn) return;
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
                return;
            }
            var consentContinue = e.target.closest(".ai-action-consent-continue");
            if (consentContinue) {
                var actionForm = consentContinue.closest("form");
                var collectionConsent = actionForm.elements.namedItem("collection_consent");
                if (!collectionConsent.checked) {
                    collectionConsent.reportValidity();
                    return;
                }
                actionForm.querySelector(".ai-action-fields").disabled = false;
                consentContinue.closest(".ai-action-consent-step").hidden = true;
                actionForm.querySelector("input[name='name']").focus();
                return;
            }
            var cancelAction = e.target.closest(".ai-action-cancel");
            if (cancelAction) {
                cancelAction.closest("form").remove();
            }
        });
        messagesEl.addEventListener("submit", function (e) {
            if (e.target.matches(".ai-inquiry-form")) {
                e.preventDefault();
                submitInquiry(e.target);
            } else if (e.target.matches(".ai-assistant-action-card")) {
                e.preventDefault();
                submitAssistantAction(e.target);
            }
        });
    }

    var consultationButton = document.getElementById("ai-consultation-action");
    var supportButton = document.getElementById("ai-support-action");
    if (consultationButton) consultationButton.addEventListener("click", function () {
        showActionForm("ai-consultation-form-template");
    });
    if (supportButton) supportButton.addEventListener("click", function () {
        showActionForm("ai-support-form-template");
    });

    function showActionForm(templateId) {
        var template = document.getElementById(templateId);
        if (!template || !template.content.firstElementChild) return;
        var actionForm = template.content.firstElementChild.cloneNode(true);
        var referenceField = actionForm.querySelector('[name="conversation_reference"]');
        if (referenceField) referenceField.value = conversationReference || createSubmissionId();
        if (actionForm.getAttribute("data-action") === "support") {
            var inquiryForm = messagesEl.querySelector(".ai-inquiry-form");
            if (inquiryForm) {
                ["name", "email", "phone"].forEach(function (fieldName) {
                    var value = inquiryForm.elements.namedItem(fieldName).value;
                    if (value) knownContactDetails[fieldName] = value;
                });
            }
            ["name", "email", "phone"].forEach(function (fieldName) {
                var inputElement = actionForm.elements.namedItem(fieldName);
                var value = knownContactDetails[fieldName];
                if (!inputElement || !value) return;
                inputElement.value = value;
                inputElement.closest("label").hidden = true;
            });
        }
        messagesEl.appendChild(actionForm);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        actionForm.querySelector(".ai-action-consent-continue").focus();
    }

    function submitAssistantAction(actionForm) {
        if (!actionForm.reportValidity()) return;
        var errorElement = actionForm.querySelector(".ai-action-form-error");
        var submitButton = actionForm.querySelector('button[type="submit"]');
        var body = new FormData(actionForm);
        var action = actionForm.getAttribute("data-action");
        var submitUrl = action === "consultation" ? consultationEndpoint : supportEndpoint;
        submitButton.disabled = true;
        errorElement.hidden = true;

        var availability = action === "consultation"
            ? postActionForm(consultationAvailabilityEndpoint, body)
            : Promise.resolve({ success: true, available: true });

        availability.then(function (availabilityResult) {
            if (!availabilityResult.success) {
                throw new Error(availabilityResult.message || "Availability could not be checked.");
            }
            if (!availabilityResult.available) {
                throw new Error(availabilityResult.message || "That time is unavailable. Please choose another.");
            }
            return postActionForm(submitUrl, body);
        }).then(function (result) {
            if (!result.success) throw new Error(result.message || "The request could not be saved.");
            var success = document.createElement("p");
            success.className = "ai-inquiry-success";
            success.textContent = result.message;
            actionForm.replaceWith(success);
        }).catch(function (error) {
            errorElement.textContent = error.message || "The request could not be completed.";
            errorElement.hidden = false;
            submitButton.disabled = false;
        });
    }

    function postActionForm(url, body) {
        return fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getCsrfToken() },
            body: body
        }).then(function (response) {
            return response.json().then(function (data) {
                if (!response.ok || !data.success) {
                    throw new Error(data.message || "Request failed (HTTP " + response.status + ").");
                }
                return data;
            });
        });
    }

    function getSelectedLanguage() {
        return languageSelect ? languageSelect.value : "auto";
    }

    function speechLocale() {
        var selected = getSelectedLanguage();
        if (selected === "hi") return "hi-IN";
        if (selected === "gu") return "gu-IN";
        if (selected === "en") return "en-IN";
        var latestMessage = conversationHistory.length
            ? conversationHistory[conversationHistory.length - 1].user
            : "";
        if (/[\u0A80-\u0AFF]/.test(latestMessage)) return "gu-IN";
        if (/[\u0900-\u097F]/.test(latestMessage)) return "hi-IN";
        return (navigator.language || "en-US");
    }

    function speakReply(text) {
        if (!speechEnabled || !("speechSynthesis" in window) || !window.SpeechSynthesisUtterance) return;
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = speechLocale();
        window.speechSynthesis.speak(utterance);
    }

    function setupVoiceControls() {
        var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (typeof Recognition === "function" && voiceButton) {
            speechRecognition = new Recognition();
            speechRecognition.continuous = false;
            speechRecognition.interimResults = false;
            voiceButton.hidden = false;
            voiceButton.addEventListener("click", function () {
                speechRecognition.lang = speechLocale();
                try {
                    speechRecognition.start();
                } catch (error) {
                    voiceStatus.textContent = "Voice input could not start. You can type your message instead.";
                    voiceStatus.hidden = false;
                }
            });
            speechRecognition.onstart = function () {
                voiceStatus.textContent = "Listening…";
                voiceStatus.hidden = false;
            };
            speechRecognition.onresult = function (event) {
                var result = event.results && event.results[0] && event.results[0][0];
                if (!result || !result.transcript) return;
                input.value = result.transcript;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                input.focus();
                voiceStatus.textContent = "Voice input added. Review it, then send.";
                voiceStatus.hidden = false;
            };
            speechRecognition.onerror = function (event) {
                var message = event.error === "not-allowed" || event.error === "service-not-allowed"
                    ? "Microphone permission was denied. You can type your message instead."
                    : "Voice input is unavailable right now. You can type your message instead.";
                voiceStatus.textContent = message;
                voiceStatus.hidden = false;
            };
            speechRecognition.onend = function () {
                if (voiceStatus.textContent === "Listening…") voiceStatus.hidden = true;
            };
        } else if (voiceStatus) {
            voiceStatus.textContent = "Voice input is not supported in this browser. You can type your message.";
            voiceStatus.hidden = false;
        }

        if ("speechSynthesis" in window && window.SpeechSynthesisUtterance && speechToggle) {
            speechToggle.hidden = false;
            speechToggle.addEventListener("click", function () {
                speechEnabled = !speechEnabled;
                speechToggle.setAttribute("aria-pressed", String(speechEnabled));
                speechToggle.textContent = speechEnabled ? "Stop reading replies" : "Read replies";
                if (!speechEnabled) window.speechSynthesis.cancel();
            });
        }
    }

    function loadBusinessInfo() {
        if (businessInfoLoaded || !businessEndpoint) return;
        businessInfoLoaded = true;
        fetch(businessEndpoint, { headers: { "Accept": "application/json" } })
            .then(function (response) {
                if (!response.ok) throw new Error("Business information unavailable.");
                return response.json();
            })
            .then(renderBusinessInfo)
            .catch(function () {
                renderBusinessInfo({ available: false, message: "Google business information is currently unavailable." });
            });
    }

    function renderBusinessInfo(info) {
        var status = document.getElementById("ai-business-status");
        var details = document.getElementById("ai-business-details");
        if (!status || !details) return;
        details.replaceChildren();
        if (!info.available) {
            status.textContent = "Status unavailable";
            details.textContent = info.message || "Verified business information is unavailable.";
            return;
        }
        status.textContent = info.status === "open" ? "Open now" : info.status === "closed" ? "Closed now" : "Current status unavailable";
        if (info.next_change) appendBusinessText(details, info.next_change);
        if (info.time_zone_label) appendBusinessText(details, "Business timezone: " + info.time_zone_label);
        if (info.address) appendBusinessText(details, info.address);
        if (info.directions_url && /^https:\/\//i.test(info.directions_url)) {
            var directions = document.createElement("a");
            directions.href = info.directions_url;
            directions.target = "_blank";
            directions.rel = "noopener noreferrer";
            directions.textContent = "Google Maps directions";
            details.appendChild(directions);
        }
        if (Array.isArray(info.regular_hours) && info.regular_hours.length) {
            var hours = document.createElement("details");
            var summary = document.createElement("summary");
            summary.textContent = "Regular hours";
            hours.appendChild(summary);
            var list = document.createElement("ul");
            info.regular_hours.forEach(function (line) {
                var item = document.createElement("li");
                item.textContent = line;
                list.appendChild(item);
            });
            hours.appendChild(list);
            details.appendChild(hours);
        } else {
            appendBusinessText(details, "Regular opening hours unavailable.");
        }
        if (Array.isArray(info.special_hours) && info.special_hours.length) {
            info.special_hours.forEach(function (line) { appendBusinessText(details, line); });
        } else {
            appendBusinessText(details, "Verified holiday hours unavailable.");
        }
    }

    function appendBusinessText(container, text) {
        var paragraph = document.createElement("p");
        paragraph.textContent = text;
        container.appendChild(paragraph);
    }

    setupVoiceControls();

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
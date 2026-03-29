(function () {
    const STORAGE_KEY = "acadexa-theme";
    const themeSelect = document.getElementById("themeSelect");
    const body = document.body;

    function applyTheme(theme) {
        const selected = theme || "heritage";
        body.setAttribute("data-theme", selected);
        if (themeSelect) {
            themeSelect.value = selected;
        }
    }

    if (themeSelect) {
        const savedTheme = window.localStorage.getItem(STORAGE_KEY);
        applyTheme(savedTheme || themeSelect.value || "heritage");

        themeSelect.addEventListener("change", function () {
            const nextTheme = themeSelect.value;
            applyTheme(nextTheme);
            window.localStorage.setItem(STORAGE_KEY, nextTheme);
        });
    }

    const form = document.getElementById("resourceForm");
    if (form) {
        const submitBtn = document.getElementById("submitBtn");
        const loaderNote = document.getElementById("loaderNote");

        const subjects = Array.from(document.querySelectorAll('input[name="subjects"]'));
        const resourceTypes = Array.from(document.querySelectorAll('input[name="resource_types"]'));

        const subjectsCount = document.getElementById("subjectsCount");
        const resourcesCount = document.getElementById("resourcesCount");
        const subjectSearch = document.getElementById("subjectSearch");
        const subjectsGroup = document.getElementById("subjectsGroup");
        const selectAllSubjects = document.getElementById("selectAllSubjects");
        const clearSubjects = document.getElementById("clearSubjects");

        function updateCount(inputs, output, singular, plural) {
            if (!output) {
                return;
            }
            const selected = inputs.filter(function (input) {
                return input.checked;
            }).length;
            output.textContent = selected + " " + (selected === 1 ? singular : plural) + " selected";
        }

        subjects.forEach(function (input) {
            input.addEventListener("change", function () {
                updateCount(subjects, subjectsCount, "subject", "subjects");
            });
        });

        resourceTypes.forEach(function (input) {
            input.addEventListener("change", function () {
                updateCount(resourceTypes, resourcesCount, "resource type", "resource types");
            });
        });

        updateCount(subjects, subjectsCount, "subject", "subjects");
        updateCount(resourceTypes, resourcesCount, "resource type", "resource types");

        if (subjectSearch && subjectsGroup) {
            subjectSearch.addEventListener("input", function () {
                const query = subjectSearch.value.trim().toLowerCase();
                const subjectLabels = Array.from(subjectsGroup.querySelectorAll("label.choice"));
                subjectLabels.forEach(function (label) {
                    const text = label.textContent.toLowerCase();
                    label.style.display = text.includes(query) ? "block" : "none";
                });
            });
        }

        if (selectAllSubjects) {
            selectAllSubjects.addEventListener("click", function () {
                subjects.forEach(function (input) {
                    input.checked = true;
                });
                updateCount(subjects, subjectsCount, "subject", "subjects");
            });
        }

        if (clearSubjects) {
            clearSubjects.addEventListener("click", function () {
                subjects.forEach(function (input) {
                    input.checked = false;
                });
                updateCount(subjects, subjectsCount, "subject", "subjects");
            });
        }

        form.addEventListener("submit", function () {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Curating...";
            }
            if (loaderNote) {
                loaderNote.classList.add("visible");
            }
        });
    }

    const downloadTrigger = document.getElementById("downloadTrigger");
    const reviewModal = document.getElementById("reviewModal");
    const closeReviewModal = document.getElementById("closeReviewModal");
    const reviewForm = document.getElementById("reviewForm");
    const reviewStatus = document.getElementById("reviewStatus");

    function toggleReviewModal(show) {
        if (!reviewModal) {
            return;
        }
        reviewModal.setAttribute("aria-hidden", show ? "false" : "true");
    }

    if (downloadTrigger && reviewModal) {
        downloadTrigger.addEventListener("click", async function (event) {
            event.preventDefault();
            const href = downloadTrigger.getAttribute("href");
            if (!href) {
                return;
            }

            const originalText = downloadTrigger.textContent;
            downloadTrigger.textContent = "Preparing PDF...";
            downloadTrigger.style.pointerEvents = "none";

            try {
                const response = await fetch(href, { method: "GET" });
                if (!response.ok) {
                    throw new Error("Unable to download PDF right now.");
                }

                const blob = await response.blob();
                const objectUrl = window.URL.createObjectURL(blob);
                const anchor = document.createElement("a");
                const disposition = response.headers.get("Content-Disposition") || "";
                const nameMatch = disposition.match(/filename=\"?([^\";]+)\"?/i);

                anchor.href = objectUrl;
                anchor.download = nameMatch ? nameMatch[1] : "acadexa_resources.pdf";
                document.body.appendChild(anchor);
                anchor.click();
                anchor.remove();
                window.URL.revokeObjectURL(objectUrl);

                window.setTimeout(function () {
                    toggleReviewModal(true);
                }, 350);
            } catch (err) {
                if (reviewStatus) {
                    reviewStatus.textContent = err.message || "Could not prepare your PDF.";
                }
            } finally {
                downloadTrigger.textContent = originalText;
                downloadTrigger.style.pointerEvents = "auto";
            }
        });
    }

    if (closeReviewModal) {
        closeReviewModal.addEventListener("click", function () {
            toggleReviewModal(false);
        });
    }

    if (reviewModal) {
        reviewModal.addEventListener("click", function (event) {
            if (event.target === reviewModal) {
                toggleReviewModal(false);
            }
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const token = reviewForm.dataset.token;
            const selected = reviewForm.querySelector('input[name="rating"]:checked');
            const commentInput = document.getElementById("reviewComment");

            if (!selected) {
                if (reviewStatus) {
                    reviewStatus.textContent = "Please choose a rating first.";
                }
                return;
            }

            const payload = {
                rating: Number(selected.value),
                comment: commentInput ? commentInput.value : ""
            };

            try {
                const response = await fetch("/review/" + token, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "Review submission failed.");
                }

                if (reviewStatus) {
                    reviewStatus.textContent = "Thanks for your feedback.";
                }
                window.setTimeout(function () {
                    toggleReviewModal(false);
                }, 900);
            } catch (err) {
                if (reviewStatus) {
                    reviewStatus.textContent = err.message || "Unable to submit review right now.";
                }
            }
        });
    }
})();

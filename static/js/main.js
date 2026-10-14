(() => {
    const menuButton = document.querySelector(".nav-toggle");
    const navigation = document.querySelector("#primary-navigation");

    if (!(menuButton instanceof HTMLButtonElement) || !(navigation instanceof HTMLElement)) {
        return;
    }

    const closeMenu = () => {
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation menu");
        navigation.classList.remove("is-open");
    };

    menuButton.addEventListener("click", () => {
        const isOpen = menuButton.getAttribute("aria-expanded") === "true";
        menuButton.setAttribute("aria-expanded", String(!isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Open navigation menu" : "Close navigation menu"
        );
        navigation.classList.toggle("is-open", !isOpen);
    });

    navigation.addEventListener("click", (event) => {
        if (event.target instanceof HTMLAnchorElement) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            menuButton.getAttribute("aria-expanded") === "true"
        ) {
            closeMenu();
            menuButton.focus();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 860) {
            closeMenu();
        }
    });

    document.querySelectorAll("[data-loading-form]").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitButton = form.querySelector('button[type="submit"]');
            if (!(submitButton instanceof HTMLButtonElement)) {
                return;
            }

            submitButton.classList.add("is-loading");
            submitButton.setAttribute("aria-busy", "true");
            submitButton.disabled = true;
            const buttonText = submitButton.querySelector("span");
            if (buttonText) {
                buttonText.textContent = "Searching…";
            }
        });
    });

    const quantityInput = document.querySelector("#requested-quantity");
    const enquiryLink = document.querySelector("[data-product-enquiry]");

    if (
        quantityInput instanceof HTMLInputElement &&
        enquiryLink instanceof HTMLAnchorElement
    ) {
        const updateEnquiryQuantity = () => {
            const quantity = quantityInput.valueAsNumber;
            if (!quantityInput.checkValidity() || !Number.isInteger(quantity)) {
                enquiryLink.removeAttribute("href");
                enquiryLink.setAttribute("aria-disabled", "true");
                enquiryLink.setAttribute("tabindex", "-1");
                enquiryLink.classList.add("is-disabled");
                return;
            }

            const enquiryUrl = new URL(enquiryLink.dataset.whatsappUrl);
            const message = `${enquiryLink.dataset.enquiryMessage}\nRequested quantity: ${quantity}.`;
            enquiryUrl.searchParams.set("text", message);
            enquiryLink.href = enquiryUrl.toString();
            enquiryLink.removeAttribute("aria-disabled");
            enquiryLink.removeAttribute("tabindex");
            enquiryLink.classList.remove("is-disabled");
        };

        quantityInput.addEventListener("input", updateEnquiryQuantity);
        updateEnquiryQuantity();
    }
})();
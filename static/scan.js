const barcodeButton = document.getElementById("capture-barcode");
const expiryButton = document.getElementById("capture-expiry");
const saveButton = document.getElementById("save-item");
const saveNextButton = document.getElementById("save-and-next");

const instruction = document.getElementById("instruction");
const barcodeMessage = document.getElementById("barcode-message");
const expiryMessage = document.getElementById("expiry-message");
const saveMessage = document.getElementById("save-message");

const barcodeInput = document.getElementById("barcode");
const nameInput = document.getElementById("name");
const brandInput = document.getElementById("brand");
const sizeInput = document.getElementById("size");
const categoryInput = document.getElementById("category");
const fullCategoryInput = document.getElementById("full-category");
const expirationDateInput = document.getElementById("expiration-date");
const quantityInput = document.getElementById("quantity");


function setLoading(button, isLoading, loadingText, normalText) {
    if (!button) {
        return;
    }

    button.disabled = isLoading;

    if (isLoading) {
        button.dataset.originalText = normalText || button.textContent;
        button.innerHTML = `<span class="button-spinner"></span>${loadingText}`;
    } else {
        button.innerHTML = button.dataset.originalText || normalText;
    }
}


function setMessage(element, text, type = "") {
    element.className = `message ${type}`;
    element.textContent = text;
}


function setMessageLoading(element, text) {
    element.className = "message loading-message";
    element.innerHTML = `<span class="inline-spinner"></span>${text}`;
}


function setScanControlsDisabled(disabled) {
    barcodeButton.disabled = disabled;
    expiryButton.disabled = disabled;
    saveButton.disabled = disabled;
    saveNextButton.disabled = disabled;
}


function fillProductFields(product) {
    nameInput.value = product.name || "";
    brandInput.value = product.brand || "";
    sizeInput.value = product.size || "";
    categoryInput.value = product.category || "";

    if (fullCategoryInput) {
        fullCategoryInput.value = product.full_category || "";
    }
}


async function fetchProductFromBarcode() {
    const barcode = barcodeInput.value.trim();

    if (!barcode) {
        setMessage(barcodeMessage, "Enter a barcode first.", "error-message");
        return;
    }

    setLoading(barcodeButton, true, "Looking up...", "Capture Barcode");
    setMessageLoading(barcodeMessage, "Looking up product details...");

    try {
        const response = await fetch(`/lookup-product/${barcode}`);
        const data = await response.json();

        if (!data.success) {
            setMessage(barcodeMessage, "Product not found. You can enter details manually.", "warning-message");
            return;
        }

        fillProductFields(data.product);
        setMessage(barcodeMessage, "Product details loaded.", "success-message");

    } catch (error) {
        console.error(error);
        setMessage(barcodeMessage, "Error loading product.", "error-message");

    } finally {
        setLoading(barcodeButton, false, "", "Capture Barcode");
    }
}


barcodeButton.addEventListener("click", async () => {
    instruction.textContent = "Capturing barcode. Keep the barcode inside the guide box.";
    setLoading(barcodeButton, true, "Scanning...", "Capture Barcode");
    setMessageLoading(barcodeMessage, "Turning on scan lighting and capturing barcode...");

    try {
        const response = await fetch("/capture-barcode", {
            method: "POST"
        });

        const data = await response.json();

        if (!data.success) {
            setMessage(barcodeMessage, data.message, "warning-message");
            return;
        }

        barcodeInput.value = data.barcode;

        if (data.product) {
            fillProductFields(data.product);
        }

        setMessage(barcodeMessage, "Barcode detected and product lookup complete.", "success-message");
        instruction.textContent = "Place the expiry date inside the guide box, then press Capture Expiry Date.";

    } catch (error) {
        console.error(error);
        setMessage(barcodeMessage, "Barcode scan failed. Please try again.", "error-message");

    } finally {
        setLoading(barcodeButton, false, "", "Capture Barcode");
    }
});


expiryButton.addEventListener("click", async () => {
    instruction.textContent = "Capturing expiry date. Keep the date text inside the guide box.";
    setLoading(expiryButton, true, "Reading...", "Capture Expiry Date");
    setMessageLoading(expiryMessage, "Capturing image and reading expiry text...");

    try {
        const response = await fetch("/capture-expiry", {
            method: "POST"
        });

        const data = await response.json();

        if (!data.success) {
            setMessage(expiryMessage, "No clear expiry date found. Please enter it manually.", "warning-message");
            return;
        }

        expirationDateInput.value = data.date;
        setMessage(expiryMessage, "Expiry date detected. Check it before saving.", "success-message");

    } catch (error) {
        console.error(error);
        setMessage(expiryMessage, "Expiry scan failed. Please try again.", "error-message");

    } finally {
        setLoading(expiryButton, false, "", "Capture Expiry Date");
    }
});


saveButton.addEventListener("click", async () => {
    await saveItem(false);
});


saveNextButton.addEventListener("click", async () => {
    await saveItem(true);
});


async function saveItem(resetAfterSave) {
    setLoading(saveButton, true, "Saving...", "Save Item");
    setLoading(saveNextButton, true, "Saving...", "Save and Scan Next");
    setMessageLoading(saveMessage, "Saving item to your inventory...");

    const payload = {
        barcode: barcodeInput.value,
        name: nameInput.value,
        brand: brandInput.value,
        size: sizeInput.value,
        category: categoryInput.value,
        full_category: fullCategoryInput ? fullCategoryInput.value : null,
        expiration_date: expirationDateInput.value || null,
        quantity: parseInt(quantityInput.value || "1")
    };

    if (!payload.barcode || !payload.name) {
        setMessage(saveMessage, "Barcode and product name are required.", "error-message");
        setLoading(saveButton, false, "", "Save Item");
        setLoading(saveNextButton, false, "", "Save and Scan Next");
        return;
    }

    try {
        const response = await fetch("/save-item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!data.success) {
            setMessage(saveMessage, "Could not save item.", "error-message");
            return;
        }

        setMessage(saveMessage, "Item saved successfully.", "success-message");

        if (resetAfterSave) {
            clearForm();
            setMessage(saveMessage, "Item saved. Ready for the next scan.", "success-message");
        }

    } catch (error) {
        console.error(error);
        setMessage(saveMessage, "Save failed. Please try again.", "error-message");

    } finally {
        setLoading(saveButton, false, "", "Save Item");
        setLoading(saveNextButton, false, "", "Save and Scan Next");
    }
}


function clearForm() {
    barcodeInput.value = "";
    nameInput.value = "";
    brandInput.value = "";
    sizeInput.value = "";
    categoryInput.value = "";

    if (fullCategoryInput) {
        fullCategoryInput.value = "";
    }

    expirationDateInput.value = "";
    quantityInput.value = "1";

    barcodeMessage.textContent = "";
    expiryMessage.textContent = "";

    instruction.textContent = "Place the barcode inside the guide box, then press Capture Barcode.";
}
function setExpiryDays(days) {
    const expiryInput = document.getElementById("expiration-date");

    if (!expiryInput) return;

    const date = new Date();

    date.setDate(date.getDate() + days);

    const formatted =
        date.getFullYear() + "-" +
        String(date.getMonth() + 1).padStart(2, "0") + "-" +
        String(date.getDate()).padStart(2, "0");

    expiryInput.value = formatted;
}
const searchInput = document.getElementById("inventory-search");
const categoryFilter = document.getElementById("category-filter");
const expiryFilter = document.getElementById("expiry-filter");
const inventoryTable = document.getElementById("inventory-table");
const noResults = document.getElementById("no-results");

function filterInventory() {
    if (!inventoryTable) return;

    const searchTerm = (searchInput.value || "").toLowerCase();
    const selectedCategory = (categoryFilter.value || "").toLowerCase();
    const selectedExpiry = expiryFilter.value || "";

    const rows = inventoryTable.querySelectorAll("tbody tr");
    let visibleCount = 0;

    rows.forEach(row => {
        const rowSearch = (row.dataset.search || "").toLowerCase();
        const rowCategory = (row.dataset.category || "").toLowerCase();
        const rowExpiry = row.dataset.expiry || "";

        const matchesSearch = rowSearch.includes(searchTerm);
        const matchesCategory = !selectedCategory || rowCategory.includes(selectedCategory);
        const matchesExpiry = !selectedExpiry || rowExpiry === selectedExpiry;

        if (matchesSearch && matchesCategory && matchesExpiry) {
            row.style.display = "";
            visibleCount += 1;
        } else {
            row.style.display = "none";
        }
    });

    if (noResults) {
        noResults.classList.toggle("hidden", visibleCount !== 0);
    }
}

if (searchInput) searchInput.addEventListener("input", filterInventory);
if (categoryFilter) categoryFilter.addEventListener("change", filterInventory);
if (expiryFilter) expiryFilter.addEventListener("change", filterInventory);
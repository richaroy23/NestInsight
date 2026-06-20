const chartFilter = document.getElementById("chartFilter");
const chartCards = document.querySelectorAll(".chart-card");

if (chartFilter) {
    chartFilter.addEventListener("change", () => {
        const selected = chartFilter.value;

        chartCards.forEach(card => {
            if (
                selected === "all" ||
                card.dataset.chart === selected
            ) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }
        });
    });
}

const columnSearch = document.getElementById("columnSearch");
const columnTags = document.querySelectorAll(".columns-box span");

if (columnSearch) {
    columnSearch.addEventListener("input", () => {
        const query = columnSearch.value.trim().toLowerCase();

        columnTags.forEach(tag => {
            const columnName = tag.textContent.trim().toLowerCase();
            tag.style.display = columnName.includes(query) ? "" : "none";
        });
    });
}
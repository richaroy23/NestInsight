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
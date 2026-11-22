(function () {
  const node = document.getElementById("chart-data");
  if (!node) return;
  const data = JSON.parse(node.textContent);

  function renderChart(id, emptyId, set, type, label) {
    if (!set.labels.length || typeof Chart === "undefined") {
      document.getElementById(id).classList.add("d-none");
      document.getElementById(emptyId).classList.remove("d-none");
      return;
    }
    new Chart(document.getElementById(id), {
      type,
      data: { labels: set.labels, datasets: [{ label, data: set.values, borderWidth: 2, tension: 0.25 }] },
      options: {
        responsive: true,
        plugins: { legend: { display: type !== "bar" } },
        scales: type === "bar" || type === "line" ? { y: { beginAtZero: true, ticks: { precision: 0 } } } : {}
      }
    });
  }
  renderChart("categoryChart", "categoryEmpty", data.category, "bar", "Complaints");
  renderChart("statusChart", "statusEmpty", data.status, "doughnut", "Complaints");
  renderChart("timeChart", "timeEmpty", data.time, "line", "Complaints");
})();

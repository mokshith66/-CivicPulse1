(function () {
  const node = document.getElementById("marker-data");
  const holder = document.getElementById("all-map");
  if (!node || !holder) return;
  if (typeof L === "undefined") {
    holder.innerHTML = '<div class="map-empty">Map library unavailable.</div>';
    return;
  }
  const data = JSON.parse(node.textContent);
  const map = L.map("all-map").setView([12.9716, 77.5946], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap"
  }).addTo(map);

  // Escape user-entered text before putting it into popup HTML (prevents XSS).
  const esc = s => String(s).replace(/[&<>"']/g,
    ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));

  const bounds = [];
  data.forEach(c => {
    const marker = L.marker([c.lat, c.lon]).addTo(map);
    marker.bindPopup(
      `<strong>${esc(c.id)}</strong><br>${esc(c.category)}<br>Status: ${esc(c.status)}` +
      `<br>${esc(c.location)}<br><a href="${esc(c.url)}">Open complaint</a>`);
    bounds.push([c.lat, c.lon]);
  });
  if (bounds.length) map.fitBounds(bounds, { padding: [25, 25] });
  else holder.insertAdjacentHTML("beforeend", '<div class="map-empty">No mapped complaints are available yet.</div>');
})();

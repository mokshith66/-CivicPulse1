(function () {
  const node = document.getElementById("map-point");
  if (!node || typeof L === "undefined") return;
  const p = JSON.parse(node.textContent);
  const map = L.map("detail-map").setView([p.lat, p.lon], 15);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap"
  }).addTo(map);
  // textContent (not innerHTML) keeps the popup safe.
  const popup = document.createElement("span");
  popup.textContent = p.id;
  L.marker([p.lat, p.lon]).addTo(map).bindPopup(popup).openPopup();
})();

(function () {
  const mapNode = document.getElementById("pick-map");
  if (!mapNode) return;
  if (typeof L === "undefined") {
    mapNode.innerHTML = '<div class="map-empty">Map library unavailable. Enter coordinates manually below.</div>';
    return;
  }
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");
  const map = L.map(mapNode).setView([12.9716, 77.5946], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap"
  }).addTo(map);
  let marker;
  function place(lat, lon) {
    latInput.value = Number(lat).toFixed(6);
    lonInput.value = Number(lon).toFixed(6);
    if (marker) marker.setLatLng([lat, lon]);
    else marker = L.marker([lat, lon]).addTo(map);
  }
  map.on("click", e => place(e.latlng.lat, e.latlng.lng));
  function fromFields() {
    const lat = Number(latInput.value), lon = Number(lonInput.value);
    if (latInput.value !== "" && lonInput.value !== "" && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) place(lat, lon);
  }
  latInput.addEventListener("change", fromFields);
  lonInput.addEventListener("change", fromFields);
  fromFields();
})();
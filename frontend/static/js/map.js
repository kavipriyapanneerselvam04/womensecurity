function initMap(mapId, zoom = 15) {
    const coords = window.wsApp.getSavedCoords() || window.wsApp.getSavedCoords({ fallbackToDefault: true });
    const map = L.map(mapId).setView([coords.lat, coords.lon], zoom);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
    return map;
}

async function fetchGeofence() {
    const response = await fetch("/geofence-settings");
    const result = await response.json();
    return result.success ? result.setting : null;
}

function listenForManualLocationUpdate(callback) {
    window.addEventListener("ws:coords", (event) => {
        callback(event.detail.lat, event.detail.lon);
    });
}

async function initDashboardMap() {
    const container = document.getElementById("map");
    if (!container) return;

    const map = initMap("map");
    const c = window.wsApp.getSavedCoords() || window.wsApp.getSavedCoords({ fallbackToDefault: true });
    const marker = L.marker([c.lat, c.lon]).addTo(map).bindPopup("Current Location");
    const setting = await fetchGeofence();
    const centerLat = setting ? Number(setting.center_latitude) : 12.9716;
    const centerLon = setting ? Number(setting.center_longitude) : 77.5946;
    const radius = setting ? Number(setting.radius_meters) : 500;
    const geofenceCircle = L.circle([centerLat, centerLon], {
        radius,
        color: "#4b79ff",
        fillColor: "#8caeff",
        fillOpacity: 0.18
    }).addTo(map);

    const updateVisuals = (lat, lon) => {
        marker.setLatLng([lat, lon]);
        map.panTo([lat, lon], { animate: true, duration: 0.5 });
    };

    listenForManualLocationUpdate(updateVisuals);
    window.wsApp.startAutomaticLocationTracking(updateVisuals);
    setInterval(async () => {
        await window.wsApp.loadDashboardSummary();
        const next = window.wsApp.getSavedCoords();
        if (next) updateVisuals(next.lat, next.lon);
    }, 6000);
}

async function initLiveTrackingMap() {
    const container = document.getElementById("liveMap");
    if (!container) return;
    const c = window.wsApp.getSavedCoords();
    const seed = c || window.wsApp.getSavedCoords({ fallbackToDefault: true });
    const map = L.map("liveMap").setView([seed.lat, seed.lon], c ? 16 : 7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    let marker = null;
    const points = c ? [[c.lat, c.lon]] : [];
    const path = L.polyline(points, { color: "#e64980", weight: 4 }).addTo(map);

    const onLocation = (lat, lon) => {
        if (!marker) {
            marker = L.marker([lat, lon]).addTo(map).bindPopup("Live user location");
        } else {
            marker.setLatLng([lat, lon]);
        }
        points.push([lat, lon]);
        if (points.length > 30) points.shift();
        path.setLatLngs(points);
        map.panTo([lat, lon], { animate: true, duration: 0.6 });
    };

    listenForManualLocationUpdate(onLocation);
    window.wsApp.startAutomaticLocationTracking(onLocation);
}

async function initGeofenceMap() {
    const container = document.getElementById("geofenceMap");
    if (!container) return;

    const map = initMap("geofenceMap", 15);
    const setting = await fetchGeofence();
    const centerLat = setting ? Number(setting.center_latitude) : 12.9716;
    const centerLon = setting ? Number(setting.center_longitude) : 77.5946;
    const radius = setting ? Number(setting.radius_meters) : 500;

    let circle = L.circle([centerLat, centerLon], {
        radius,
        color: "#4b79ff",
        fillColor: "#a3bdff",
        fillOpacity: 0.28
    }).addTo(map);

    const c = window.wsApp.getSavedCoords() || window.wsApp.getSavedCoords({ fallbackToDefault: true });
    const marker = L.marker([c.lat, c.lon]).addTo(map);

    window.wsApp.startAutomaticLocationTracking((lat, lon) => {
        marker.setLatLng([lat, lon]);
    });

    window.addEventListener("ws:geofence-changed", async () => {
        const updated = await fetchGeofence();
        if (!updated) return;
        map.removeLayer(circle);
        circle = L.circle([Number(updated.center_latitude), Number(updated.center_longitude)], {
            radius: Number(updated.radius_meters),
            color: "#4b79ff",
            fillColor: "#a3bdff",
            fillOpacity: 0.28
        }).addTo(map);
    });
}

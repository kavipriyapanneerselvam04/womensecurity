const API_BASE = "";
const DEFAULT_COORDS = { lat: 12.9716, lon: 77.5946 };
let locationWatchId = null;
let trackingBootPromise = null;
let manualRefreshWatchId = null;
let manualRefreshTimerId = null;
let pendingFreshLocationSince = 0;
const LIVE_LOCATION_MAX_AGE_MS = 2 * 60 * 1000;
const COUNTRY_CODES = [
    { code: "+91", label: "India (+91)" },
    { code: "+1", label: "United States (+1)" },
    { code: "+44", label: "United Kingdom (+44)" },
    { code: "+61", label: "Australia (+61)" },
    { code: "+971", label: "UAE (+971)" },
    { code: "+81", label: "Japan (+81)" },
    { code: "+49", label: "Germany (+49)" },
    { code: "+33", label: "France (+33)" },
    { code: "+39", label: "Italy (+39)" },
    { code: "+34", label: "Spain (+34)" },
    { code: "+65", label: "Singapore (+65)" },
    { code: "+63", label: "Philippines (+63)" },
];

function initCountryDropdown(selectId, defaultCode = "+91") {
    const select = document.getElementById(selectId);
    if (!select || select.options.length > 0) return;
    COUNTRY_CODES.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.code;
        opt.textContent = item.label;
        if (item.code === defaultCode) opt.selected = true;
        select.appendChild(opt);
    });
}

function initPhoneCountrySelects() {
    initCountryDropdown("phoneCountryCode");
    initCountryDropdown("regCountryCode");
    initCountryDropdown("newUserCountryCode");
}

function buildInternationalPhone(numberInputId, countrySelectId) {
    const raw = (document.getElementById(numberInputId)?.value || "").trim();
    if (!raw) return "";
    if (raw.startsWith("+")) return raw.replace(/\s+/g, "");
    const code = (document.getElementById(countrySelectId)?.value || "+91").trim();
    const digits = raw.replace(/\D/g, "");
    return digits ? `${code}${digits}` : "";
}

function getCurrentUser() {
    const raw = localStorage.getItem("ws_user");
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (_) {
        return null;
    }
}

function setCurrentUser(user) {
    localStorage.setItem("ws_user", JSON.stringify(user));
}

function getSavedCoords(options = {}) {
    const { fallbackToDefault = false } = options;
    const raw = localStorage.getItem("ws_coords");
    if (!raw) return fallbackToDefault ? DEFAULT_COORDS : null;
    try {
        const parsed = JSON.parse(raw);
        if (typeof parsed.lat === "number" && typeof parsed.lon === "number") return parsed;
    } catch (_) {}
    return fallbackToDefault ? DEFAULT_COORDS : null;
}

function saveCoords(lat, lon) {
    localStorage.setItem("ws_coords", JSON.stringify({ lat, lon }));
    const latInput = document.getElementById("manualLatitude");
    const lonInput = document.getElementById("manualLongitude");
    if (latInput) latInput.value = Number(lat).toFixed(6);
    if (lonInput) lonInput.value = Number(lon).toFixed(6);
    window.dispatchEvent(new CustomEvent("ws:coords", { detail: { lat, lon } }));
}

function clearSavedCoords() {
    localStorage.removeItem("ws_coords");
}

function setGpsState(text) {
    const statusEl = document.getElementById("gpsState");
    if (statusEl) statusEl.textContent = text;
}

function setCurrentCoordsText(lat, lon) {
    const coordsEl = document.getElementById("currentCoords");
    if (!coordsEl) return;
    if (typeof lat === "number" && typeof lon === "number") {
        coordsEl.textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
        return;
    }
    coordsEl.textContent = "--";
}

function setCurrentPlaceText(place) {
    const placeEl = document.getElementById("currentPlace");
    if (placeEl) placeEl.textContent = place || "--";
}

function setLocationMeta(position) {
    const metaEl = document.getElementById("locationMeta");
    if (!metaEl) return;
    if (!position?.coords) {
        metaEl.textContent = "--";
        return;
    }
    const accuracy = Math.round(position.coords.accuracy || 0);
    const timestamp = new Date(position.timestamp || Date.now()).toLocaleTimeString();
    metaEl.textContent = `Accuracy: ${accuracy}m | Updated: ${timestamp}`;
}

function clearVisibleLocation(reason = "Waiting for current GPS location...") {
    clearSavedCoords();
    setCurrentCoordsText();
    setCurrentPlaceText("--");
    setLocationMeta(null);
    setGpsState(reason);
}

function toDateInputValue(value) {
    if (!value) return "";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${d.getFullYear()}-${month}-${day}`;
}

async function resolvePlaceName(lat, lon) {
    try {
        const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
        const response = await fetch(url, {
            headers: {
                Accept: "application/json",
            },
        });
        if (!response.ok) return null;
        const data = await response.json();
        return data.display_name || null;
    } catch (_) {
        return null;
    }
}

async function apiRequest(path, method = "GET", body = null) {
    const options = { method, headers: { "Content-Type": "application/json" } };
    if (body) options.body = JSON.stringify(body);
    const response = await fetch(`${API_BASE}${path}`, options);
    return response.json();
}

async function ensureSession() {
    const result = await apiRequest("/me");
    if (!result.success) {
        window.location.href = "/";
        return null;
    }
    setCurrentUser(result.user);
    const label = document.getElementById("currentUserName");
    if (label) label.textContent = result.user.name;
    return result.user;
}

async function logoutUser() {
    await apiRequest("/logout", "POST");
    localStorage.removeItem("ws_user");
    window.location.href = "/";
}

async function deleteAccountPermanently() {
    const ok = window.confirm("This will permanently delete your account, contacts, alerts and history. Continue?");
    if (!ok) return;
    const result = await apiRequest("/api/account", "DELETE");
    if (result.success) {
        alert("Account deleted permanently.");
        localStorage.removeItem("ws_user");
        window.location.href = "/";
        return;
    }
    alert(result.message || "Failed to delete account.");
}

async function loginUser(event) {
    event.preventDefault();
    const name = document.getElementById("name").value.trim();
    const phone = buildInternationalPhone("phone", "phoneCountryCode");
    const result = await apiRequest("/login", "POST", { name, phone });
    const messageEl = document.getElementById("loginMessage");
    if (result.success) {
        setCurrentUser(result.user);
        window.location.href = "/dashboard";
        return;
    }
    messageEl.textContent = result.message || "Login failed";
}

async function registerUser(event) {
    event.preventDefault();
    const name = document.getElementById("regName").value.trim();
    const phone = buildInternationalPhone("regPhone", "regCountryCode");
    const result = await apiRequest("/register", "POST", { name, phone });
    const messageEl = document.getElementById("registerMessage");
    if (result.success) {
        messageEl.style.color = "#1f8b50";
        messageEl.textContent = "Registration successful. Please login.";
        setTimeout(() => {
            window.location.href = "/";
        }, 900);
        return;
    }
    messageEl.style.color = "#c52851";
    messageEl.textContent = result.message || "Registration failed";
}

async function updateLocation(lat, lon) {
    const result = await apiRequest("/update-location", "POST", { latitude: lat, longitude: lon });
    if (result.success) {
        saveCoords(lat, lon);
        setCurrentCoordsText(lat, lon);
        const place = await resolvePlaceName(lat, lon);
        setCurrentPlaceText(place);
        renderGeofenceStatus(result.geofence);
    }
    return result;
}

async function applyBrowserPosition(position, stateText = "Current location captured.", onDone = null) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    pendingFreshLocationSince = 0;
    setGpsState(stateText);
    setLocationMeta(position);
    await updateLocation(lat, lon);
    if (onDone) onDone(lat, lon);
}

function renderGeofenceStatus(geofence) {
    const geofenceStatusEl = document.getElementById("geofenceStatus");
    if (!geofenceStatusEl || !geofence) return;
    if (geofence.inside) {
        geofenceStatusEl.innerHTML = `<span class="tag tag-ok">Inside Safe Zone</span> ${geofence.distance_meters}m from center`;
    } else {
        geofenceStatusEl.innerHTML = `<span class="tag tag-danger">Boundary Exceeded</span> ${geofence.distance_meters}m from center`;
    }
}

function showCurrentLocation(onDone) {
    if (!navigator.geolocation) {
        setGpsState("Browser geolocation not supported.");
        return;
    }
    if (manualRefreshWatchId !== null) {
        navigator.geolocation.clearWatch(manualRefreshWatchId);
        manualRefreshWatchId = null;
    }
    if (manualRefreshTimerId !== null) {
        clearTimeout(manualRefreshTimerId);
        manualRefreshTimerId = null;
    }

    pendingFreshLocationSince = Date.now();
    setGpsState("Refreshing current location...");
    setCurrentCoordsText();
    setCurrentPlaceText("--");
    setLocationMeta(null);

    let bestPosition = null;
    const finishRefresh = async () => {
        if (manualRefreshWatchId !== null) {
            navigator.geolocation.clearWatch(manualRefreshWatchId);
            manualRefreshWatchId = null;
        }
        if (manualRefreshTimerId !== null) {
            clearTimeout(manualRefreshTimerId);
            manualRefreshTimerId = null;
        }
        if (bestPosition) {
            await applyBrowserPosition(bestPosition, "Fresh browser location captured.", onDone);
        } else {
            clearVisibleLocation("Could not get a fresh location fix from Chrome.");
        }
    };

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            bestPosition = position;
            await applyBrowserPosition(position, "Current location captured.", onDone);
        },
        () => {
            clearVisibleLocation("GPS permission denied. Allow location in browser site settings.");
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );

    manualRefreshWatchId = navigator.geolocation.watchPosition(
        (position) => {
            if (!bestPosition || (position.coords.accuracy || Number.MAX_SAFE_INTEGER) < (bestPosition.coords.accuracy || Number.MAX_SAFE_INTEGER)) {
                bestPosition = position;
            }
        },
        () => {},
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );

    manualRefreshTimerId = setTimeout(() => {
        finishRefresh();
    }, 12000);
}

function getGeolocationErrorMessage(error) {
    if (!error) return "Unable to fetch current location.";
    if (error.code === 1) {
        return "Location access blocked in browser or Windows settings.";
    }
    if (error.code === 2) {
        return "Location unavailable. Check internet, GPS, or Windows location services.";
    }
    if (error.code === 3) {
        return "Location request timed out. Try again with GPS or Wi-Fi enabled.";
    }
    return error.message || "Unable to fetch current location.";
}

function isFreshLocationTimestamp(timestamp) {
    if (!timestamp) return false;
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime())) return false;
    return Date.now() - parsed.getTime() <= LIVE_LOCATION_MAX_AGE_MS;
}

function isNewerThanPendingRequest(timestamp) {
    if (!pendingFreshLocationSince) return true;
    if (!timestamp) return false;
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime())) return false;
    return parsed.getTime() >= pendingFreshLocationSince;
}

function showGpsHelp() {
    alert(
        "Enable GPS Location:\n1. Click the lock/info icon near URL.\n2. Set Location to Allow.\n3. Reload page.\n4. Click Show Current Location."
    );
}

async function updateManualLocation() {
    const latInput = document.getElementById("manualLatitude");
    const lonInput = document.getElementById("manualLongitude");
    const messageEl = document.getElementById("manualLocationMessage");
    if (!latInput || !lonInput) return;

    const lat = Number(latInput.value);
    const lon = Number(lonInput.value);

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
        if (messageEl) messageEl.textContent = "Enter valid latitude and longitude values.";
        return;
    }

    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        if (messageEl) messageEl.textContent = "Latitude must be between -90 and 90, longitude between -180 and 180.";
        return;
    }

    if (messageEl) messageEl.textContent = "Updating location...";
    const result = await updateLocation(lat, lon);
    if (result.success) {
        setGpsState("Manual location active");
        if (messageEl) messageEl.textContent = "Location updated successfully.";
    } else if (messageEl) {
        messageEl.textContent = result.message || "Failed to update location.";
    }
}

function attachLiveBrowserLocation(onUpdate) {
    if (!navigator.geolocation) return;
    if (locationWatchId !== null) return;
    locationWatchId = navigator.geolocation.watchPosition(
        async (position) => {
            await applyBrowserPosition(position, "Live browser GPS active", onUpdate);
        },
        (error) => {
            clearVisibleLocation(getGeolocationErrorMessage(error));
        },
        { enableHighAccuracy: true, maximumAge: 0, timeout: 15000 }
    );
}

async function startAutomaticLocationTracking(onUpdate) {
    if (!navigator.geolocation) {
        setGpsState("Browser geolocation not supported.");
        return false;
    }

    if (trackingBootPromise) {
        await trackingBootPromise;
        return true;
    }

    trackingBootPromise = (async () => {
        try {
            if (navigator.permissions?.query) {
                const permission = await navigator.permissions.query({ name: "geolocation" });
                if (permission.state === "denied") {
                    clearVisibleLocation("Location blocked. Enable it in Chrome and Windows location settings.");
                    return;
                }
                if (permission.state === "prompt") {
                    setGpsState("Allow location access to detect your current place automatically.");
                }
            } else {
                setGpsState("Requesting your current location...");
            }
        } catch (_) {
            setGpsState("Requesting your current location...");
        }

        await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    await applyBrowserPosition(position, "Current location captured.", onUpdate);
                    resolve();
                },
                (error) => {
                    clearVisibleLocation(getGeolocationErrorMessage(error));
                    resolve();
                },
                { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
            );
        });

        if (locationWatchId === null) {
            locationWatchId = navigator.geolocation.watchPosition(
                async (position) => {
                    await applyBrowserPosition(position, "Live browser GPS active", onUpdate);
                },
                (error) => {
                    clearVisibleLocation(getGeolocationErrorMessage(error));
                },
                { enableHighAccuracy: true, maximumAge: 0, timeout: 15000 }
            );
        }
    })();

    await trackingBootPromise;
    return true;
}

async function simulateMovement() {
    const c = getSavedCoords({ fallbackToDefault: true });
    const nextLat = c.lat + (Math.random() - 0.5) * 0.0022;
    const nextLon = c.lon + (Math.random() - 0.5) * 0.0022;
    await updateLocation(nextLat, nextLon);
    await loadDashboardSummary();
}

async function triggerPanicAlert() {
    const c = getSavedCoords({ fallbackToDefault: true });
    const result = await apiRequest("/panic-alert", "POST", { latitude: c.lat, longitude: c.lon });
    const el = document.getElementById("actionMessage");
    el.textContent = result.success ? `Panic alert sent #${result.alert_id}` : (result.message || "Panic alert failed");
    await loadDashboardSummary();
}

async function triggerFallAlert() {
    const c = getSavedCoords({ fallbackToDefault: true });
    const result = await apiRequest("/fall-alert", "POST", { latitude: c.lat, longitude: c.lon });
    const el = document.getElementById("actionMessage");
    el.textContent = result.success ? `Fall alert sent #${result.alert_id}` : (result.message || "Fall alert failed");
    await loadDashboardSummary();
}

async function loadDashboardSummary() {
    const result = await apiRequest("/dashboard-summary");
    if (!result.success) return;
    const counts = result.counts;
    const totalEl = document.getElementById("totalAlerts");
    const fallEl = document.getElementById("fallAlerts");
    const boundaryEl = document.getElementById("boundaryAlerts");
    const panicEl = document.getElementById("panicAlerts");
    if (totalEl) totalEl.textContent = counts.total_alerts;
    if (fallEl) fallEl.textContent = counts.fall_alerts;
    if (boundaryEl) boundaryEl.textContent = counts.boundary_alerts;
    if (panicEl) panicEl.textContent = counts.panic_alerts;

    const recentList = document.getElementById("recentAlerts");
    if (recentList) {
        recentList.innerHTML = "";
        result.recent_alerts.forEach((a) => {
            const li = document.createElement("li");
            li.innerHTML = `<b>${a.alert_type}</b> | ${a.latitude}, ${a.longitude} <span class="muted">(${a.timestamp})</span>`;
            recentList.appendChild(li);
        });
    }

    if (result.latest_location) {
        if (
            isFreshLocationTimestamp(result.latest_location.timestamp) &&
            isNewerThanPendingRequest(result.latest_location.timestamp)
        ) {
            const lat = Number(result.latest_location.latitude);
            const lon = Number(result.latest_location.longitude);
            saveCoords(lat, lon);
            setCurrentCoordsText(lat, lon);
            const place = await resolvePlaceName(lat, lon);
            setCurrentPlaceText(place);
            pendingFreshLocationSince = 0;
        } else {
            clearVisibleLocation("Stored location is old. Waiting for fresh live GPS location...");
        }
    } else {
        clearVisibleLocation("No live location found yet. Waiting for current GPS location...");
    }
}

async function loadAlertsTable(tableId) {
    const tbody = document.getElementById(tableId);
    if (!tbody) return;
    const result = await apiRequest("/alerts");
    if (!result.success) return;
    tbody.innerHTML = "";
    result.alerts.forEach((a) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${a.id}</td>
            <td>${a.alert_type}</td>
            <td>${a.user_phone || "-"}</td>
            <td>${a.latitude}</td>
            <td>${a.longitude}</td>
            <td>${a.timestamp}</td>
            <td>${a.status}</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadUsersTable() {
    const tbody = document.getElementById("usersTableBody");
    if (!tbody) return;
    const result = await apiRequest("/users");
    if (!result.success) return;
    tbody.innerHTML = "";
    result.users.forEach((u, idx) => {
        const row = document.createElement("tr");
        const notify = Number(u.notification_enabled) === 1 ? "Yes" : "No";
        row.innerHTML = `
            <td>${idx + 1}</td>
            <td>${u.name}</td>
            <td>${u.role}</td>
            <td>${u.phone}</td>
            <td>${notify}</td>
            <td><button class="btn btn-danger btn-sm" onclick="wsApp.deleteContact(${u.id})">Delete</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function addUser(event) {
    event.preventDefault();
    const name = document.getElementById("newUserName").value.trim();
    const phone = buildInternationalPhone("newUserPhone", "newUserCountryCode");
    const role = document.getElementById("newUserRole").value;
    const notification_enabled = document.getElementById("newUserNotify").checked;
    const result = await apiRequest("/users", "POST", { name, phone, role, notification_enabled });
    const msgEl = document.getElementById("userFormMessage");
    msgEl.textContent = result.success ? "Contact added successfully." : (result.message || "Failed to add contact");
    if (result.success) {
        document.getElementById("addUserForm").reset();
        await loadUsersTable();
    }
}

async function deleteContact(contactId) {
    const ok = window.confirm("Delete this contact?");
    if (!ok) return;
    const result = await apiRequest(`/users/${contactId}`, "DELETE");
    const msgEl = document.getElementById("userFormMessage");
    msgEl.textContent = result.success ? "Contact deleted successfully." : (result.message || "Delete failed");
    if (result.success) {
        await loadUsersTable();
    }
}

async function loadGeofenceSettings() {
    const result = await apiRequest("/geofence-settings");
    if (!result.success) return;
    const setting = result.setting;
    const radiusInput = document.getElementById("radiusMeters");
    const centerLatInput = document.getElementById("centerLatitude");
    const centerLonInput = document.getElementById("centerLongitude");
    if (radiusInput) radiusInput.value = setting.radius_meters;
    if (centerLatInput) centerLatInput.value = setting.center_latitude;
    if (centerLonInput) centerLonInput.value = setting.center_longitude;
}

async function loadProfilePage() {
    await ensureSession();
    const profileRes = await apiRequest("/api/profile");
    if (!profileRes.success) return;
    const user = profileRes.profile;
    if (!user) return;
    const nameEl = document.getElementById("profileName");
    const phoneEl = document.getElementById("profilePhone");
    const roleEl = document.getElementById("profileRole");
    const initialEl = document.getElementById("profileInitial");
    const photoEl = document.getElementById("profilePhoto");
    const nameInputEl = document.getElementById("profileNameInput");
    const dobInputEl = document.getElementById("profileDobInput");
    const parentInputEl = document.getElementById("profileParentInput");
    const wardenInputEl = document.getElementById("profileWardenInput");
    const collegeAddressInputEl = document.getElementById("profileCollegeAddressInput");
    const homeAddressInputEl = document.getElementById("profileHomeAddressInput");
    if (nameEl) nameEl.textContent = user.name;
    if (nameInputEl) nameInputEl.value = user.name || "";
    if (phoneEl) phoneEl.textContent = user.phone;
    if (roleEl) roleEl.textContent = user.role;
    if (initialEl) initialEl.textContent = (user.name || "S").trim().charAt(0).toUpperCase();
    if (photoEl) {
        if (user.profile_photo) {
            photoEl.src = user.profile_photo;
            photoEl.style.display = "block";
            if (initialEl) initialEl.style.display = "none";
        } else {
            photoEl.style.display = "none";
            if (initialEl) initialEl.style.display = "grid";
        }
    }
    if (dobInputEl) dobInputEl.value = toDateInputValue(user.date_of_birth);
    if (parentInputEl) parentInputEl.value = user.parent_name || "";
    if (wardenInputEl) wardenInputEl.value = user.warden_name || "";
    if (collegeAddressInputEl) collegeAddressInputEl.value = user.college_address || "";
    if (homeAddressInputEl) homeAddressInputEl.value = user.home_address || user.address || "";

    const contactsRes = await apiRequest("/users");
    if (contactsRes.success) {
        const countEl = document.getElementById("profileContactCount");
        if (countEl) countEl.textContent = contactsRes.users.length;
    }
}

async function saveProfileDetails() {
    const message = document.getElementById("profileAddressMessage");
    const payload = {
        name: document.getElementById("profileNameInput")?.value?.trim() || null,
        date_of_birth: document.getElementById("profileDobInput")?.value || null,
        parent_name: document.getElementById("profileParentInput")?.value?.trim() || "",
        warden_name: document.getElementById("profileWardenInput")?.value?.trim() || "",
        college_address: document.getElementById("profileCollegeAddressInput")?.value?.trim() || "",
        home_address: document.getElementById("profileHomeAddressInput")?.value?.trim() || "",
    };
    payload.address = payload.home_address;
    const result = await apiRequest("/api/profile", "PUT", payload);
    if (result.success) {
        if (message) message.textContent = "Profile details saved.";
        await loadProfilePage();
    } else {
        if (message) message.textContent = result.message || "Failed to save profile details.";
    }
}

async function uploadProfilePhoto(event) {
    const input = event.target;
    if (!input.files || input.files.length === 0) return;
    const formData = new FormData();
    formData.append("photo", input.files[0]);
    const response = await fetch("/api/profile-photo", {
        method: "POST",
        body: formData,
    });
    const result = await response.json();
    const message = document.getElementById("profileAddressMessage");
    if (result.success) {
        if (message) message.textContent = "Profile photo updated.";
        await loadProfilePage();
    } else if (message) {
        message.textContent = result.message || "Failed to upload photo.";
    }
}

function setBoundaryFromCurrentLocation() {
    showCurrentLocation(async (lat, lon) => {
        const radius = Number(document.getElementById("radiusMeters").value || 500);
        const result = await apiRequest("/geofence-settings", "POST", {
            center_latitude: lat,
            center_longitude: lon,
            radius_meters: radius,
        });
        const msg = document.getElementById("geofenceMessage");
        if (result.success) {
            const centerLatInput = document.getElementById("centerLatitude");
            const centerLonInput = document.getElementById("centerLongitude");
            if (centerLatInput) centerLatInput.value = Number(lat).toFixed(6);
            if (centerLonInput) centerLonInput.value = Number(lon).toFixed(6);
            if (msg) msg.textContent = "Boundary center set to your current real location.";
        } else if (msg) {
            msg.textContent = result.message || "Failed to set boundary from current location.";
        }
        window.dispatchEvent(new CustomEvent("ws:geofence-changed"));
    });
}

async function saveBoundarySettings(event) {
    event.preventDefault();
    const centerLat = Number(document.getElementById("centerLatitude").value);
    const centerLon = Number(document.getElementById("centerLongitude").value);
    const radius = Number(document.getElementById("radiusMeters").value);
    const result = await apiRequest("/geofence-settings", "POST", {
        center_latitude: centerLat,
        center_longitude: centerLon,
        radius_meters: radius,
    });
    const msg = document.getElementById("geofenceMessage");
    msg.textContent = result.success ? "Geo-fence settings saved." : (result.message || "Failed to save");
    window.dispatchEvent(new CustomEvent("ws:geofence-changed"));
}

function applyTheme(theme) {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("ws_theme", theme);
    const labels = document.querySelectorAll(".theme-icon");
    labels.forEach((label) => {
        label.innerHTML = theme === "dark" ? "&#9728;" : "&#9789;";
    });
}

function initTheme() {
    initPhoneCountrySelects();
    const stored = localStorage.getItem("ws_theme") || "light";
    applyTheme(stored);
    const toggles = document.querySelectorAll(".theme-toggle");
    toggles.forEach((btn) => {
        btn.addEventListener("click", () => {
            const next = document.body.getAttribute("data-theme") === "dark" ? "light" : "dark";
            applyTheme(next);
        });
    });
}

async function shareLiveLocation() {
    const messageEl = document.getElementById("shareLocationMessage");
    const coords = getSavedCoords();
    if (!coords) {
        if (messageEl) messageEl.textContent = "Current live location is not available yet.";
        return;
    }

    const mapsUrl = `https://www.google.com/maps?q=${encodeURIComponent(coords.lat)},${encodeURIComponent(coords.lon)}`;
    const place = document.getElementById("currentPlace")?.textContent?.trim();
    const shareText = place && place !== "--"
        ? `My current live location: ${place}\n${mapsUrl}`
        : `My current live location: ${coords.lat.toFixed(6)}, ${coords.lon.toFixed(6)}\n${mapsUrl}`;

    try {
        if (navigator.share) {
            await navigator.share({
                title: "SafeHer Live Location",
                text: shareText,
                url: mapsUrl,
            });
            if (messageEl) messageEl.textContent = "Live location shared successfully.";
            return;
        }

        if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(shareText);
            if (messageEl) messageEl.textContent = "Live location link copied. You can paste it to share.";
            return;
        }

        window.prompt("Copy and share this live location link:", shareText);
        if (messageEl) messageEl.textContent = "Live location link is ready to share.";
    } catch (_) {
        if (messageEl) messageEl.textContent = "Unable to share right now. Please try again.";
    }
}

window.wsApp = {
    loginUser,
    registerUser,
    ensureSession,
    logoutUser,
    deleteAccountPermanently,
    getSavedCoords,
    updateLocation,
    showCurrentLocation,
    updateManualLocation,
    attachLiveBrowserLocation,
    startAutomaticLocationTracking,
    simulateMovement,
    triggerPanicAlert,
    triggerFallAlert,
    loadDashboardSummary,
    loadAlertsTable,
    loadUsersTable,
    addUser,
    deleteContact,
    loadGeofenceSettings,
    setBoundaryFromCurrentLocation,
    saveBoundarySettings,
    loadProfilePage,
    saveProfileDetails,
    uploadProfilePhoto,
    showGpsHelp,
    initTheme,
    shareLiveLocation
};

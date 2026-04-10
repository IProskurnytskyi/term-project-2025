const App = (() => {
    const API_BASE = "/api/v1";

    const elements = {};

    function cacheElements() {
        elements.sidebar = document.getElementById("sidebar");
        elements.sidebarToggle = document.getElementById("sidebar-toggle");
        elements.tabs = document.querySelectorAll(".tab");
        elements.tabFields = document.getElementById("tab-fields");
        elements.tabDraw = document.getElementById("tab-draw");
        elements.fieldsList = document.getElementById("fields-list");
        elements.btnRefresh = document.getElementById("btn-refresh");
        elements.geojsonOutput = document.getElementById("geojson-output");
        elements.btnCreateField = document.getElementById("btn-create-field");
        elements.drawStatus = document.getElementById("draw-status");
    }

    function init() {
        cacheElements();

        const map = MapModule.init();
        DrawModule.init(map, MapModule.getDrawnItems());

        setupSidebarToggle();
        setupTabs();
        setupDrawHandlers();
        setupRefresh();

        loadFields();
    }

    // ---- Sidebar ----

    function setupSidebarToggle() {
        elements.sidebarToggle.addEventListener("click", toggleSidebar);

        let openBtn = document.querySelector(".sidebar-open-btn");
        if (!openBtn) {
            openBtn = document.createElement("button");
            openBtn.className = "sidebar-open-btn";
            openBtn.innerHTML = "&rsaquo;";
            openBtn.title = "Open sidebar";
            document.getElementById("app").appendChild(openBtn);
        }
        openBtn.addEventListener("click", toggleSidebar);
    }

    function toggleSidebar() {
        elements.sidebar.classList.toggle("collapsed");
        setTimeout(() => MapModule.getMap().invalidateSize(), 300);
    }

    // ---- Tabs ----

    function setupTabs() {
        elements.tabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                elements.tabs.forEach((tabEl) => tabEl.classList.remove("active"));
                tab.classList.add("active");

                const target = tab.dataset.tab;
                document.querySelectorAll(".tab-content").forEach((content) => {
                    content.classList.toggle("active", content.id === `tab-${target}`);
                });
            });
        });
    }

    // ---- Draw handlers ----

    function setupDrawHandlers() {
        DrawModule.onShapeDrawn((geometry) => {
            if (geometry) {
                elements.geojsonOutput.value = JSON.stringify(geometry, null, 2);
                elements.btnCreateField.disabled = false;

                switchToTab("draw");
            } else {
                elements.geojsonOutput.value = "";
                elements.btnCreateField.disabled = true;
            }
            setDrawStatus("", "");
        });

        elements.btnCreateField.addEventListener("click", handleCreateField);
    }

    function switchToTab(tabName) {
        elements.tabs.forEach((tab) => {
            tab.classList.toggle("active", tab.dataset.tab === tabName);
        });
        document.querySelectorAll(".tab-content").forEach((content) => {
            content.classList.toggle("active", content.id === `tab-${tabName}`);
        });
    }

    async function handleCreateField() {
        const geometry = DrawModule.getCurrentGeoJSON();
        if (!geometry) return;

        elements.btnCreateField.disabled = true;
        setDrawStatus('<span class="spinner"></span> Creating field...', "");

        try {
            const response = await fetch(`${API_BASE}/fields/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ boundary: geometry }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const field = await response.json();
            setDrawStatus("Field created successfully!", "success");

            DrawModule.clearDrawn(MapModule.getDrawnItems());
            elements.geojsonOutput.value = "";

            await loadFields();
            MapModule.focusField(field.id);
            switchToTab("fields");
        } catch (error) {
            setDrawStatus(`Error: ${error.message}`, "error");
            elements.btnCreateField.disabled = false;
        }
    }

    function setDrawStatus(message, type) {
        elements.drawStatus.innerHTML = message;
        elements.drawStatus.className = `status-message ${type}`;
    }

    // ---- Fields loading ----

    function setupRefresh() {
        elements.btnRefresh.addEventListener("click", loadFields);
    }

    async function loadFields() {
        elements.fieldsList.innerHTML = '<p class="placeholder"><span class="spinner"></span> Loading...</p>';

        try {
            const response = await fetch(`${API_BASE}/fields/?size=50`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            const fields = data.items || [];

            renderFieldsList(fields);
            renderFieldsOnMap(fields);
        } catch (error) {
            elements.fieldsList.innerHTML = `<p class="placeholder">Failed to load fields: ${error.message}</p>`;
        }
    }

    function renderFieldsList(fields) {
        if (fields.length === 0) {
            elements.fieldsList.innerHTML = '<p class="placeholder">No fields yet. Draw a polygon on the map to create one.</p>';
            return;
        }

        elements.fieldsList.innerHTML = "";

        fields.forEach((field) => {
            const card = document.createElement("div");
            card.className = "field-card";

            const createdDate = new Date(field.creation_date).toLocaleString();
            const shortId = field.id.substring(0, 8) + "...";

            let imagesHtml = "";
            if (field.image_url || field.ndvi_url) {
                imagesHtml += '<div class="field-card-images">';
                if (field.image_url) {
                    imagesHtml += `
                        <div class="field-card-preview">
                            <div class="preview-label">RGB</div>
                            <img src="${field.image_url}" alt="Satellite" loading="lazy" />
                        </div>`;
                }
                if (field.ndvi_url) {
                    imagesHtml += `
                        <div class="field-card-preview">
                            <div class="preview-label preview-label-ndvi">NDVI</div>
                            <img src="${field.ndvi_url}" alt="NDVI" loading="lazy" />
                        </div>`;
                }
                imagesHtml += "</div>";
            }

            card.innerHTML = `
                <div class="field-card-id" title="${field.id}">${shortId}</div>
                <div class="field-card-date">Created: ${createdDate}</div>
                ${imagesHtml}
                <div class="field-card-weather" id="weather-${field.id}"></div>
                <div class="field-card-actions">
                    <button class="btn btn-sm btn-satellite btn-fetch-rgb">RGB</button>
                    <button class="btn btn-sm btn-ndvi btn-fetch-ndvi">NDVI</button>
                    <button class="btn btn-sm btn-weather btn-fetch-weather">Weather</button>
                    <button class="btn btn-sm btn-danger btn-delete">Delete</button>
                </div>
            `;

            card.addEventListener("click", (event) => {
                if (event.target.tagName === "BUTTON") return;
                MapModule.focusField(field.id);
            });

            card.querySelector(".btn-fetch-rgb").addEventListener("click", () => fetchSatelliteImage(field));
            card.querySelector(".btn-fetch-ndvi").addEventListener("click", () => fetchNdviImage(field));
            card.querySelector(".btn-fetch-weather").addEventListener("click", () => fetchWeather(field, card));
            card.querySelector(".btn-delete").addEventListener("click", () => deleteField(field));

            elements.fieldsList.appendChild(card);
        });
    }

    function renderFieldsOnMap(fields) {
        MapModule.clearFields();
        fields.forEach((field) => {
            MapModule.addFieldToMap(field, {
                onSatellite: fetchSatelliteImage,
                onNdvi: fetchNdviImage,
                onWeather: fetchWeatherPopup,
                onDelete: deleteField,
            });
        });
    }

    // ---- Field actions ----

    async function fetchSatelliteImage(field) {
        if (!confirm("Fetch satellite image for this field? This may take a moment.")) return;

        try {
            const response = await fetch(`${API_BASE}/satellite-image/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ boundary: field.boundary }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const updatedField = await response.json();
            await loadFields();
            MapModule.focusField(updatedField.id);
        } catch (error) {
            alert(`Failed to fetch satellite image: ${error.message}`);
        }
    }

    async function fetchNdviImage(field) {
        if (!confirm("Fetch NDVI image for this field? This may take a moment.")) return;

        try {
            const response = await fetch(`${API_BASE}/ndvi/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ boundary: field.boundary }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const updatedField = await response.json();
            await loadFields();
            MapModule.focusField(updatedField.id);
        } catch (error) {
            alert(`Failed to fetch NDVI image: ${error.message}`);
        }
    }

    async function fetchWeather(field, card) {
        const weatherContainer = card.querySelector(".field-card-weather");
        weatherContainer.innerHTML = '<span class="spinner"></span> Loading weather...';

        try {
            const response = await fetch(`${API_BASE}/fields/${field.id}/weather`);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const weather = await response.json();
            weatherContainer.innerHTML = renderWeatherPanel(weather);
        } catch (error) {
            weatherContainer.innerHTML = `<span class="status-message error">Failed: ${error.message}</span>`;
        }
    }

    function renderWeatherPanel(weather) {
        const current = weather.current;
        const daily = weather.daily;

        let forecastHtml = daily.slice(0, 5).map((day) => `
            <div class="forecast-day">
                <div class="forecast-date">${day.date.slice(5)}</div>
                <div class="forecast-desc">${day.weather_description}</div>
                <div class="forecast-temp">${day.temperature_min}° / ${day.temperature_max}°</div>
                <div class="forecast-rain">${day.precipitation_sum} mm</div>
            </div>
        `).join("");

        return `
            <div class="weather-panel">
                <div class="weather-current">
                    <div class="weather-temp">${current.temperature}°C</div>
                    <div class="weather-desc">${current.weather_description}</div>
                    <div class="weather-details">
                        <span>Feels ${current.apparent_temperature}°C</span>
                        <span>Humidity ${current.humidity}%</span>
                        <span>Wind ${current.wind_speed} km/h</span>
                        <span>Rain ${current.precipitation} mm</span>
                    </div>
                </div>
                <div class="weather-forecast">${forecastHtml}</div>
            </div>
        `;
    }

    async function fetchWeatherPopup(field) {
        try {
            const response = await fetch(`${API_BASE}/fields/${field.id}/weather`);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            const weather = await response.json();
            const current = weather.current;
            alert(
                `Weather at field:\n` +
                `${current.weather_description}\n` +
                `Temperature: ${current.temperature}°C (feels ${current.apparent_temperature}°C)\n` +
                `Humidity: ${current.humidity}%\n` +
                `Wind: ${current.wind_speed} km/h\n` +
                `Precipitation: ${current.precipitation} mm`
            );
        } catch (error) {
            alert(`Failed to fetch weather: ${error.message}`);
        }
    }

    async function deleteField(field) {
        if (!confirm(`Delete field ${field.id.substring(0, 8)}...?`)) return;

        try {
            const response = await fetch(`${API_BASE}/fields/${field.id}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            await loadFields();
        } catch (error) {
            alert(`Failed to delete field: ${error.message}`);
        }
    }

    // ---- Start ----

    document.addEventListener("DOMContentLoaded", init);

    return { loadFields };
})();
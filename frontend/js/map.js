const MapModule = (() => {
    let map;
    let fieldsLayer;
    let drawnItems;

    const UKRAINE_CENTER = [48.5, 31.5];
    const DEFAULT_ZOOM = 6;

    const FIELD_STYLE = {
        color: "#3b82f6",
        weight: 2,
        opacity: 0.8,
        fillColor: "#3b82f6",
        fillOpacity: 0.15,
    };

    const FIELD_HOVER_STYLE = {
        weight: 3,
        fillOpacity: 0.3,
    };

    function init() {
        map = L.map("map", {
            center: UKRAINE_CENTER,
            zoom: DEFAULT_ZOOM,
            zoomControl: true,
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19,
        }).addTo(map);

        fieldsLayer = L.featureGroup().addTo(map);
        drawnItems = L.featureGroup().addTo(map);

        return map;
    }

    function getMap() {
        return map;
    }

    function getDrawnItems() {
        return drawnItems;
    }

    function getFieldsLayer() {
        return fieldsLayer;
    }

    function clearFields() {
        fieldsLayer.clearLayers();
    }

    function addFieldToMap(field, { onSatellite, onNdvi, onSar, onNdviCompare, onWeather, onDelete }) {
        if (!field.boundary || !field.boundary.coordinates) return null;

        const geoJsonLayer = L.geoJSON(field.boundary, {
            style: () => ({ ...FIELD_STYLE }),
        });

        geoJsonLayer.eachLayer((layer) => {
            layer.fieldId = field.id;

            layer.on("mouseover", () => layer.setStyle(FIELD_HOVER_STYLE));
            layer.on("mouseout", () => layer.setStyle(FIELD_STYLE));

            const popupContent = buildPopupContent(field, { onSatellite, onNdvi, onSar, onNdviCompare, onWeather, onDelete });
            layer.bindPopup(popupContent, { maxWidth: 350 });
        });

        geoJsonLayer.addTo(fieldsLayer);
        return geoJsonLayer;
    }

    function buildPopupContent(field, { onSatellite, onNdvi, onSar, onNdviCompare, onWeather, onDelete }) {
        const container = document.createElement("div");
        container.className = "field-popup";

        const createdDate = new Date(field.creation_date).toLocaleString();
        const shortId = field.id.substring(0, 8) + "...";

        container.innerHTML = `
            <p><strong>ID:</strong> <span class="popup-id" title="${field.id}">${shortId}</span></p>
            <p><strong>Created:</strong> ${createdDate}</p>
        `;

        if (field.image_url || field.ndvi_url || field.sar_change_url) {
            const imagesContainer = document.createElement("div");
            imagesContainer.className = "popup-images";

            if (field.image_url) {
                const wrapper = document.createElement("div");
                wrapper.className = "popup-image-container";
                wrapper.innerHTML = `<div class="preview-label">RGB</div><img src="${field.image_url}" alt="Satellite" loading="lazy" />`;
                imagesContainer.appendChild(wrapper);
            }

            if (field.ndvi_url) {
                const wrapper = document.createElement("div");
                wrapper.className = "popup-image-container";
                wrapper.innerHTML = `<div class="preview-label preview-label-ndvi">NDVI</div><img src="${field.ndvi_url}" alt="NDVI" loading="lazy" />`;
                imagesContainer.appendChild(wrapper);
            }

            if (field.sar_change_url) {
                const wrapper = document.createElement("div");
                wrapper.className = "popup-image-container";
                wrapper.innerHTML = `<div class="preview-label preview-label-sar">SAR</div><img src="${field.sar_change_url}" alt="SAR Change" loading="lazy" />`;
                imagesContainer.appendChild(wrapper);
            }

            container.appendChild(imagesContainer);
        }

        const actions = document.createElement("div");
        actions.className = "popup-actions";

        const satelliteBtn = document.createElement("button");
        satelliteBtn.className = "btn btn-sm btn-satellite";
        satelliteBtn.textContent = "RGB";
        satelliteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            onSatellite(field);
        });

        const ndviBtn = document.createElement("button");
        ndviBtn.className = "btn btn-sm btn-ndvi";
        ndviBtn.textContent = "NDVI";
        ndviBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            onNdvi(field);
        });

        const sarBtn = document.createElement("button");
        sarBtn.className = "btn btn-sm btn-sar";
        sarBtn.textContent = "SAR";
        sarBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            togglePopupSarForm(field, sarSection, onSar);
        });

        const ndviCompareBtn = document.createElement("button");
        ndviCompareBtn.className = "btn btn-sm btn-ndvi-compare";
        ndviCompareBtn.textContent = "NDVI Compare";
        ndviCompareBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            togglePopupNdviCompareForm(field, ndviCompareSection, onNdviCompare);
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-sm btn-danger";
        deleteBtn.textContent = "Delete";
        deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            onDelete(field);
        });

        actions.appendChild(satelliteBtn);
        actions.appendChild(ndviBtn);
        actions.appendChild(sarBtn);
        actions.appendChild(ndviCompareBtn);
        actions.appendChild(deleteBtn);
        container.appendChild(actions);

        const sarSection = document.createElement("div");
        sarSection.className = "popup-sar";
        container.appendChild(sarSection);

        const ndviCompareSection = document.createElement("div");
        ndviCompareSection.className = "popup-ndvi-compare";
        container.appendChild(ndviCompareSection);

        const weatherContainer = document.createElement("div");
        weatherContainer.className = "popup-weather";

        const weatherBtn = document.createElement("button");
        weatherBtn.className = "btn btn-sm btn-weather";
        weatherBtn.textContent = "Load weather";
        weatherBtn.addEventListener("click", async (event) => {
            event.stopPropagation();
            weatherBtn.disabled = true;
            weatherBtn.innerHTML = '<span class="spinner"></span> Loading...';
            const weatherData = await onWeather(field);
            if (weatherData) {
                const current = weatherData.current;
                weatherContainer.innerHTML = `
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
                    </div>`;
            } else {
                weatherBtn.textContent = "Load weather";
                weatherBtn.disabled = false;
            }
        });

        weatherContainer.appendChild(weatherBtn);
        container.appendChild(weatherContainer);

        return container;
    }

    function togglePopupSarForm(field, sarSection, onSar) {
        if (sarSection.querySelector(".sar-form")) {
            sarSection.innerHTML = "";
            return;
        }

        const today = new Date().toISOString().split("T")[0];
        const threeMonthsAgo = new Date(Date.now() - 90 * 86400000).toISOString().split("T")[0];
        const sixMonthsAgo = new Date(Date.now() - 180 * 86400000).toISOString().split("T")[0];
        const nineMonthsAgo = new Date(Date.now() - 270 * 86400000).toISOString().split("T")[0];

        sarSection.innerHTML = `
            <div class="sar-form">
                <div class="sar-period">
                    <span class="sar-period-label">Before period</span>
                    <input type="date" class="sar-input sar-before-start" value="${nineMonthsAgo}" />
                    <input type="date" class="sar-input sar-before-end" value="${sixMonthsAgo}" />
                </div>
                <div class="sar-period">
                    <span class="sar-period-label">After period</span>
                    <input type="date" class="sar-input sar-after-start" value="${threeMonthsAgo}" />
                    <input type="date" class="sar-input sar-after-end" value="${today}" />
                </div>
                <button class="btn btn-sm btn-sar btn-run-sar">Run SAR Change Detection</button>
                <div class="sar-status"></div>
            </div>
        `;

        sarSection.querySelector(".btn-run-sar").addEventListener("click", async (event) => {
            event.stopPropagation();
            const beforeStart = sarSection.querySelector(".sar-before-start").value;
            const beforeEnd = sarSection.querySelector(".sar-before-end").value;
            const afterStart = sarSection.querySelector(".sar-after-start").value;
            const afterEnd = sarSection.querySelector(".sar-after-end").value;
            const statusEl = sarSection.querySelector(".sar-status");
            const runBtn = sarSection.querySelector(".btn-run-sar");

            if (!beforeStart || !beforeEnd || !afterStart || !afterEnd) {
                statusEl.innerHTML = '<span class="status-message error">Please fill all date fields</span>';
                return;
            }

            runBtn.disabled = true;
            statusEl.innerHTML = '<span class="spinner"></span> Computing SAR change detection...';

            try {
                await onSar(field, beforeStart, beforeEnd, afterStart, afterEnd);
            } catch (error) {
                statusEl.innerHTML = `<span class="status-message error">Error: ${error.message}</span>`;
                runBtn.disabled = false;
            }
        });
    }

    function togglePopupNdviCompareForm(field, section, onNdviCompare) {
        if (section.querySelector(".ndvi-compare-form")) {
            section.innerHTML = "";
            return;
        }

        const today = new Date().toISOString().split("T")[0];
        const threeMonthsAgo = new Date(Date.now() - 90 * 86400000).toISOString().split("T")[0];

        section.innerHTML = `
            <div class="ndvi-compare-form">
                <div class="ndvi-compare-period">
                    <span class="ndvi-compare-period-label">Before period</span>
                    <input type="date" class="ndvi-compare-input ndvi-before-start" value="2021-06-01" />
                    <input type="date" class="ndvi-compare-input ndvi-before-end" value="2021-09-01" />
                </div>
                <div class="ndvi-compare-period">
                    <span class="ndvi-compare-period-label">After period</span>
                    <input type="date" class="ndvi-compare-input ndvi-after-start" value="${threeMonthsAgo}" />
                    <input type="date" class="ndvi-compare-input ndvi-after-end" value="${today}" />
                </div>
                <button class="btn btn-sm btn-ndvi-compare btn-run-ndvi-compare">Run NDVI Comparison</button>
                <div class="ndvi-compare-status"></div>
                <div class="ndvi-compare-results"></div>
            </div>
        `;

        section.querySelector(".btn-run-ndvi-compare").addEventListener("click", async (event) => {
            event.stopPropagation();
            const beforeStart = section.querySelector(".ndvi-before-start").value;
            const beforeEnd = section.querySelector(".ndvi-before-end").value;
            const afterStart = section.querySelector(".ndvi-after-start").value;
            const afterEnd = section.querySelector(".ndvi-after-end").value;
            const statusEl = section.querySelector(".ndvi-compare-status");
            const resultsEl = section.querySelector(".ndvi-compare-results");
            const runBtn = section.querySelector(".btn-run-ndvi-compare");

            if (!beforeStart || !beforeEnd || !afterStart || !afterEnd) {
                statusEl.innerHTML = '<span class="status-message error">Please fill all date fields</span>';
                return;
            }

            runBtn.disabled = true;
            statusEl.innerHTML = '<span class="spinner"></span> Computing NDVI comparison...';
            resultsEl.innerHTML = "";

            try {
                const data = await onNdviCompare(field, beforeStart, beforeEnd, afterStart, afterEnd);
                statusEl.innerHTML = "";
                resultsEl.innerHTML = `
                    <div class="ndvi-compare-images">
                        <div class="ndvi-compare-image">
                            <div class="preview-label preview-label-ndvi">Before</div>
                            <img src="${data.ndvi_before_url}" alt="NDVI Before" loading="lazy" />
                        </div>
                        <div class="ndvi-compare-image">
                            <div class="preview-label preview-label-ndvi">After</div>
                            <img src="${data.ndvi_after_url}" alt="NDVI After" loading="lazy" />
                        </div>
                        <div class="ndvi-compare-image ndvi-compare-diff">
                            <div class="preview-label preview-label-ndvi-diff">Difference</div>
                            <img src="${data.ndvi_diff_url}" alt="NDVI Difference" loading="lazy" />
                        </div>
                    </div>
                `;
                runBtn.disabled = false;
            } catch (error) {
                statusEl.innerHTML = `<span class="status-message error">Error: ${error.message}</span>`;
                runBtn.disabled = false;
            }
        });
    }

    function focusField(fieldId) {
        fieldsLayer.eachLayer((group) => {
            group.eachLayer((layer) => {
                if (layer.fieldId === fieldId) {
                    map.fitBounds(layer.getBounds(), { padding: [50, 50] });
                    layer.openPopup();
                }
            });
        });
    }

    return {
        init,
        getMap,
        getDrawnItems,
        getFieldsLayer,
        clearFields,
        addFieldToMap,
        focusField,
    };
})();
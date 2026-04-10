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

    function addFieldToMap(field, { onSatellite, onNdvi, onWeather, onDelete }) {
        if (!field.boundary || !field.boundary.coordinates) return null;

        const geoJsonLayer = L.geoJSON(field.boundary, {
            style: () => ({ ...FIELD_STYLE }),
        });

        geoJsonLayer.eachLayer((layer) => {
            layer.fieldId = field.id;

            layer.on("mouseover", () => layer.setStyle(FIELD_HOVER_STYLE));
            layer.on("mouseout", () => layer.setStyle(FIELD_STYLE));

            const popupContent = buildPopupContent(field, { onSatellite, onNdvi, onWeather, onDelete });
            layer.bindPopup(popupContent, { maxWidth: 350 });
        });

        geoJsonLayer.addTo(fieldsLayer);
        return geoJsonLayer;
    }

    function buildPopupContent(field, { onSatellite, onNdvi, onWeather, onDelete }) {
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

        const weatherBtn = document.createElement("button");
        weatherBtn.className = "btn btn-sm btn-weather";
        weatherBtn.textContent = "Weather";
        weatherBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            onWeather(field);
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
        actions.appendChild(weatherBtn);
        actions.appendChild(deleteBtn);
        container.appendChild(actions);

        return container;
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
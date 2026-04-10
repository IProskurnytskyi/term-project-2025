const DrawModule = (() => {
    let drawControl;
    let currentGeoJSON = null;
    let onShapeDrawnCallback = null;

    function init(map, drawnItems) {
        drawControl = new L.Control.Draw({
            position: "topright",
            draw: {
                polygon: {
                    allowIntersection: false,
                    showArea: true,
                    shapeOptions: {
                        color: "#22c55e",
                        weight: 2,
                        fillOpacity: 0.2,
                    },
                },
                rectangle: {
                    shapeOptions: {
                        color: "#22c55e",
                        weight: 2,
                        fillOpacity: 0.2,
                    },
                },
                polyline: false,
                circle: false,
                marker: false,
                circlemarker: false,
            },
            edit: {
                featureGroup: drawnItems,
                remove: true,
            },
        });

        map.addControl(drawControl);

        map.on(L.Draw.Event.CREATED, (event) => {
            drawnItems.clearLayers();
            const layer = event.layer;
            drawnItems.addLayer(layer);

            currentGeoJSON = layerToGeoJSON(layer);

            if (onShapeDrawnCallback) {
                onShapeDrawnCallback(currentGeoJSON);
            }
        });

        map.on(L.Draw.Event.DELETED, () => {
            currentGeoJSON = null;
            if (onShapeDrawnCallback) {
                onShapeDrawnCallback(null);
            }
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                currentGeoJSON = layerToGeoJSON(layer);
                if (onShapeDrawnCallback) {
                    onShapeDrawnCallback(currentGeoJSON);
                }
            });
        });
    }

    function layerToGeoJSON(layer) {
        const geojson = layer.toGeoJSON();
        return geojson.geometry;
    }

    function getCurrentGeoJSON() {
        return currentGeoJSON;
    }

    function clearDrawn(drawnItems) {
        drawnItems.clearLayers();
        currentGeoJSON = null;
        if (onShapeDrawnCallback) {
            onShapeDrawnCallback(null);
        }
    }

    function onShapeDrawn(callback) {
        onShapeDrawnCallback = callback;
    }

    return {
        init,
        getCurrentGeoJSON,
        clearDrawn,
        onShapeDrawn,
    };
})();
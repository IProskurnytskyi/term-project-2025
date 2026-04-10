# Satellite Image Field Service

## Description
A FastAPI-based platform for monitoring agricultural fields using Sentinel-2 satellite imagery. Includes an interactive web frontend for drawing field boundaries, viewing satellite images, and managing fields.

### Key Features:
- **Interactive Map (Frontend)**: Leaflet-based web interface for drawing polygons, viewing fields, and fetching satellite images.
- **Field Boundary Management**: Stores field geometries and spatial data using PostGIS.
- **Satellite Image Integration**: Fetches Sentinel-2 RGB images via Google Earth Engine with cloud cover filtering (<20%).
- **NDVI Vegetation Index**: Calculates NDVI (Normalized Difference Vegetation Index) from Sentinel-2 B8/B4 bands. Visualized with a red-to-green color scale indicating vegetation health.
- **Weather Integration**: Current weather and 7-day forecast for any field location via Open-Meteo API (temperature, humidity, wind, precipitation).
- **Image Expiration Handling**: Automatically refreshes expired or missing field imagery (50-minute TTL).
- **Database**: PostgreSQL with PostGIS for spatial data.
- **Deployment**: Docker-ready with Alembic migrations.

## Installation
1. **Clone the Repository**:
    ```bash
    git clone <link-to-repository>
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd /path/to/your/project
    ```

3. **Setting Up Environment Variables**:
    - Copy the sample environment configuration file and configure the necessary variables:
        ```bash
        cp .env.sample .env
        ```

4. **Install Dependencies using poetry**:
    ```bash
    poetry install
    ```

5. **Install Pre-Commit Hooks**:
    ```bash
    poetry run pre-commit install
    ```

6. **Set Up the Database**:
    - Make sure PostgreSQL is installed and PostGIS extension is enabled.
    - Create the required database.
    - Enable PostGIS inside the database:
        ```bash
        CREATE EXTENSION postgis;
        ```

7. **Generate and Apply Migrations**:
    - Generate the initial migration:
        ```bash
        poetry run alembic revision --autogenerate -m "initial"
        ```
    - Apply the migration to the database:
        ```bash
        poetry run alembic upgrade head
        ```

8. **Running the Application**:
    ```bash
    poetry run uvicorn src.main:create_app --host 0.0.0.0 --port 8000 --reload
    ```
    - Frontend: http://localhost:8000/
    - API docs (Swagger): http://localhost:8000/docs

## Project Structure
- **`src/main.py`**: Entry point for the FastAPI application. Serves the frontend via StaticFiles.
- **`src/models/`**: SQLAlchemy models.
- **`src/api/schemas/`**: Pydantic schemas for request and response validation.
- **`src/api/routers/`**: Route handlers for field and satellite endpoints.
- **`src/database/postgres/crud/`**: Data handling operations.
- **`src/services/google_earth.py`**: Google Earth Engine integration for Sentinel-2 RGB and NDVI imagery.
- **`src/services/weather.py`**: Open-Meteo API integration for weather data.
- **`src/common/exceptions.py`**: Custom exceptions.
- **`src/utils/`**: Utility functions.
- **`frontend/`**: Web frontend (HTML/CSS/JS).
    - `index.html` — Single-page app entry point.
    - `js/map.js` — Leaflet map initialization and field rendering.
    - `js/draw.js` — Polygon/rectangle drawing tools and GeoJSON export.
    - `js/app.js` — Main controller: API calls, sidebar, field CRUD.
    - `css/style.css` — Dark theme styling.

## Additional Notes
- **Alembic**: Used for managing database migrations.
- Satellite images are fetched from **Sentinel-2** (COPERNICUS/S2_HARMONIZED) via Google Earth Engine.
- **NDVI** is calculated as `(B8 - B4) / (B8 + B4)` using `normalizedDifference` on Sentinel-2 bands.
- Images with >20% cloud cover are filtered out automatically.
- Image expiration is handled via the `expiration_time` field (50-minute TTL).
- Weather data is fetched from **Open-Meteo** (free, no API key required) based on the field boundary centroid.

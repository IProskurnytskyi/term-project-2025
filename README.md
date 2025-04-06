# 🌾 Satellite Image Field Service

## 🚀 Description
The **Satellite Image Field Service** is a FastAPI-based backend that manages agricultural fields, boundaries, and associated satellite imagery.

> 💡 You can use [geojson.io](https://geojson.io/) to create and export field boundaries in GeoJSON format for image retrieval.

### Key Features:
- **Field Boundary Management**: Stores field geometries and spatial data using PostGIS.
- **Satellite Image Integration**: Fetches and updates Sentinel satellite images using Google Earth Engine.
- **Image Expiration Handling**: Automatically refreshes expired or missing field imagery.
- **Database**: Uses PostgreSQL with PostGIS for handling spatial data.
- **Deployment**: Easily deployable locally or on any cloud platform. Designed with Docker and Alembic for smooth development and deployment.

## 📦 Installation
1. **Clone the Repository**:
    ```bash
    git clone <link-to-repository>
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd /path/to/your/project
    ```

3. **Setting Up Environment Variables**:
    - **Create Your `.env` File**:
        Copy the sample environment configuration file to create your `.env` file and configure the necessary environment variables:
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

8. **Running the FastAPI Application**:
    - Start the FastAPI server locally for development:
        ```bash
        poetry run uvicorn src.main:create_app --host 0.0.0.0 --port 8000 --reload
        ```

## 🗂 Project Structure
- **`src/main.py`**: Entry point for the FastAPI application.
- **`src/models/`**: Contains the SQLAlchemy models.
- **`src/api/schemas/`**: Pydantic schemas for request and response data validation.
- **`src/api/routers/`**: Directory containing route handlers for different endpoints.
- **`src/database/postgres/crud/`**: Data handling operations.
- **`src/common/exceptions.py`**: Custom exceptions for raising in crud operations and catching in routers.
- **`src/utils/`**: Util functions that can be used throughout the project.

## 📌 Additional Notes
- **Alembic**: Used for managing database migrations; keep track of schema changes.
- Satellite images are fetched using **get_latest_sentinel_image** integration.
- Image expiration is handled in the DB via the expiration_time field (50-minute TTL logic).

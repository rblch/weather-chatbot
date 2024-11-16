# TWC Chatbot

## Introduction
TWC Chatbot provides weather forecasts for cities using the OpenWeatherMap API. 
The chatbot is designed to interact with users, detect city names from their questions, and return relevant weather information.

## Installation

### Prerequisites
- Docker and Docker Compose installed.
- Python 3.9 or higher (if not using Docker).

### Using Docker (Recommended)

1. Download and extract the repository from the shared file link.

2. Navigate to the project directory:
    ```sh
    cd weather-chatbot
    ```

3. Ensure the `.env` file is present in the project root directory and filled with the required environment variables.

4. Build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```

### Without Docker

1. Download and extract the repository from the shared file link.

2. Navigate to the project directory:
    ```sh
    cd weather-chatbot
    ```

3. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

5. Ensure the `.env` file is present in the project root directory and filled with the required environment variables.

6. Run the application:
    ```sh
    streamlit run main.py
    ```

## Configuration

### Docker Configuration
- Docker is set up to use a `Dockerfile` and `docker-compose.yml` to build and run the application.

## Usage
- After starting the application, navigate to `http://localhost:8501` in your web browser to access the chatbot interface.
- Interact with the chatbot by asking about the weather for different cities.

## Important note
This repository includes a `.env` file with environment variables and API keys to ensure the application runs smoothly without additional setup. 
Please handle these credentials with care and do not share them publicly. The keys will be deactivated after the grading.
# Run with Docker

## Define environment variables

Copy the `.env.example` file to `.env` and fill in the values.

```bash
cp .env.example .env
```

## Run the app with Docker (no Docker Compose)

### Build the Docker image

Use the `build.sh` script to build the Docker images.

```bash
./build.sh
```

### Run the Docker container

Use the `run.sh` script to run the Docker containers.

```bash
./run.sh
```

#### Streamlit

The Streamlit app will be available at `http://localhost:8501`.

#### Serving (Flask)

This will start the Flask app on port `8000` (unless you changed the `PORT` in the `.env` file).

The app will be available at `http://localhost:8000`.

You can see logs on route `http://localhost:8000/logs`.

### Stop the Docker container

Call the `stop.sh` script to stop the Docker containers.

```bash
./stop.sh
```

## Run the app with Docker Composes

### Start the Docker-compose stack

Use the native Docker Compose command to start the stack.

```bash
docker-compose up -d
```

As above, the app will be available at `http://localhost:8000`.

#### Rebuild the Docker images

If you need to force a rebuild of the images, you can use the `--build` flag.

```bash
docker-compose up -d --build
```

### Stop the Docker-compose stack

Use the native Docker Compose command to stop the stack.

```bash
docker-compose down
```

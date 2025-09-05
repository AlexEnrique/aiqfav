# aiqfav API
API to manage customers and their favorite products.

> Not ready for production. To prepare for production, you would need to:
> - gitignore the `.env` file and add appropriate envs
> - add a production database
> - add a production Redis
> - add a production build stage to Docker file
> - build and push the Docker image to a registry


## Dependencies

- Python 3.12
- Docker
- Docker Compose
- make
- uv
- pre-commit

## How to run

1. Install Docker and Docker Compose
2. Install `make` to run Makefile commands
3. Install `uv` (https://docs.astral.sh/uv/getting-started/installation/)
4. (Development only) Install `pre-commit` (https://pre-commit.com/) to run pre-commit hooks
5. Install project dependencies with `make install`
6. Run the project with `make dev` (this will build the project with Docker and run all containers in `docker-compose.yml`)
7. To view all available commands, run `make help`

### Alternative way to run the project
```bash
docker compose up -d --build
```

## Create an admin customer/user
Some endpoints require an admin customer. You can create one with the following command:
```bash
make create-admin
```

This will prompt you for the name, email and password of the admin customer.


## API Documentation
The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
or [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc). **Powered by FastAPI**.

You can also get the OpenAPI specification file accessing [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json).


## Tests
To run the tests, run `make test`.
To run the tests with coverage, run `make cov` The report will be available at `htmlcov/index.html`.


## Current coverage
Current coverage is `86%`.

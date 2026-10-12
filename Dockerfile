# Dockerfile: builds the image for the python app
# small python 3.11 image
FROM python:3.11-slim

# get uv to install packages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# work inside /app folder
WORKDIR /app

# copy package files first so install is cached
COPY pyproject.toml uv.lock ./
# install exact versions from uv.lock, skip dev packages
RUN uv sync --frozen --no-dev

# copy rest of the project
COPY . .

# use python from .venv
ENV PATH="/app/.venv/bin:$PATH"

# run main.py when container starts
CMD ["python", "src/main.py"]
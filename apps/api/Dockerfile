FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry==1.8.2

# Copy the entire monorepo (context is repo root)
COPY packages/engine /app/packages/engine
COPY apps/api /app/apps/api

# Move to API directory
WORKDIR /app/apps/api

# Configure poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-root

EXPOSE 80

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
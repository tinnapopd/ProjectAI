#!/bin/bash

set -e

VERSION="v1.5"

docker login

# Build the backend
echo "Building backend..."
docker build --platform linux/amd64 -t google-ai-backend:latest ./backend
docker tag google-ai-backend:latest teetinnapop/cicd:google-ai-backend-$VERSION
docker push teetinnapop/cicd:google-ai-backend-$VERSION

# Build the frontend
echo "Building frontend..."
docker build --platform linux/amd64 -t google-ai-frontend:latest ./frontend
docker tag google-ai-frontend:latest teetinnapop/cicd:google-ai-frontend-$VERSION
docker push teetinnapop/cicd:google-ai-frontend-$VERSION
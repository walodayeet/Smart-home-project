#!/bin/sh
# Install Python and Node.js dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend && npm install

echo "Building frontend..."
npm run build

echo "Build complete!"

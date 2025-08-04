#!/bin/bash

# Build script for React Admin Panel
echo "Building Seafood Store Admin Panel..."

# Navigate to admin panel directory
cd admin-panel

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build for production
echo "Building for production..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Admin panel built successfully!"
    echo "📂 Build files are in admin-panel/build/"
    echo "🚀 The admin panel will be available at /adminpanel when the backend is running"
else
    echo "❌ Build failed!"
    exit 1
fi

echo "Done!"
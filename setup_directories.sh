#!/bin/bash

# Use BASE_PATH from environment or set default
BASE_PATH=${BASE_PATH:-/data}

# Create directories
mkdir -p "$BASE_PATH/config"
mkdir -p "$BASE_PATH/data"
mkdir -p "$BASE_PATH/uploads"

# Set permissions (adjust user/group if needed)
chmod 755 "$BASE_PATH"
chmod 755 "$BASE_PATH/config"
chmod 755 "$BASE_PATH/data"
chmod 755 "$BASE_PATH/uploads"

echo "Directories created and permissions set:"
echo "Base path: $BASE_PATH"
echo "Config: $BASE_PATH/config"
echo "Data: $BASE_PATH/data"
echo "Uploads: $BASE_PATH/uploads"

# Check if directories exist and are writable
for dir in "config" "data" "uploads"; do
    if [ -w "$BASE_PATH/$dir" ]; then
        echo "✓ $dir directory is created and writable"
    else
        echo "✗ Error: $dir directory is not writable"
    fi
done 
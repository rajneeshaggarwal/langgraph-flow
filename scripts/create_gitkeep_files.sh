#!/bin/bash

# Script to create .gitkeep files in empty directories that should be preserved in git

echo "Creating .gitkeep files in empty directories..."

# List of directories that should have .gitkeep files
directories=(
    "airflow/logs"
    "airflow/plugins"
    "airflow/config"
    "uploads"
    "static"
    "database/migrations"
    "backend/api"
    "backend/core"
    "frontend/public"
    "frontend/src/components"
    "frontend/src/hooks"
    "frontend/src/utils"
    "frontend/src/services"
    "frontend/src/types"
)

# Create directories and .gitkeep files
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created directory: $dir"
    fi
    
    if [ ! -f "$dir/.gitkeep" ]; then
        touch "$dir/.gitkeep"
        echo "Created .gitkeep in: $dir"
    else
        echo ".gitkeep already exists in: $dir"
    fi
done

echo "Done! All .gitkeep files have been created."
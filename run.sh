#!/bin/bash

# Function to delete images after successful archiving
delete_images() {
    echo "Deleting images from generated_images..."
    rm -f generated_images/*
    echo "Images deleted."
}

# Function to build the Go binary if it doesn't exist
build_go_binary() {
    if [ ! -f archiver ]; then
        echo "Building Go archiver binary..."
        go build -o archiver archiver.go
        if [ $? -eq 0 ]; then
            echo "Go archiver binary built successfully."
        else
            echo "Failed to build Go archiver binary."
            exit 1
        fi
    else
        echo "Go archiver binary already present. Skipping build."
    fi
}

# Check if "generated_images" directory is empty
if [ "$(ls -A generated_images)" ]; then
    echo "Generated images found."
    build_go_binary
    if ./archiver; then
        echo "Archiving completed successfully."
        delete_images
    else
        echo "Archiving failed."
    fi
else
    echo "No generated images found. Running Python script to generate images..."
    if python main.py; then
        echo "Generating images completed."
        build_go_binary
        if ./archiver; then
            echo "Image generation and archiving completed successfully."
            delete_images
        else
            echo "Archiving failed."
        fi
    else
        echo "Image generation failed."
    fi
fi

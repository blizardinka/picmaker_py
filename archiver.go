package main

import (
	"archive/zip"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sync"
)

// Function to add a single file to the zip archive
func addFileToZip(wg *sync.WaitGroup, mutex *sync.Mutex, zipWriter *zip.Writer, filePath string) {
	defer wg.Done()

	// Open the file to be added to the zip
	file, err := os.Open(filePath)
	if err != nil {
		fmt.Printf("Failed to open file %s: %v\n", filePath, err)
		return
	}
	defer file.Close()

	// Lock before writing to the zip to ensure no concurrent writes
	mutex.Lock()
	defer mutex.Unlock()

	// Create a writer for this file in the zip
	baseName := filepath.Base(filePath)
	zipFileWriter, err := zipWriter.Create(baseName)
	if err != nil {
		fmt.Printf("Failed to create zip entry for %s: %v\n", filePath, err)
		return
	}

	// Copy the file data to the zip entry
	_, err = io.Copy(zipFileWriter, file)
	if err != nil {
		fmt.Printf("Failed to write file %s to zip: %v\n", filePath, err)
		return
	}

	fmt.Printf("Successfully added %s to zip\n", baseName)
}

func main() {
	imageDir := "generated_images"
	zipFileName := "images.zip"

	// Create a zip file
	zipFile, err := os.Create(zipFileName)
	if err != nil {
		fmt.Printf("Failed to create zip file: %v\n", err)
		return
	}
	defer zipFile.Close()

	// Create a new zip writer
	zipWriter := zip.NewWriter(zipFile)
	defer func() {
		if err := zipWriter.Close(); err != nil {
			fmt.Printf("Error closing zip writer: %v\n", err)
		}
	}()

	var wg sync.WaitGroup
	var mutex sync.Mutex // Mutex to prevent concurrent writes

	// Walk through the directory to get all image files
	err = filepath.Walk(imageDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		wg.Add(1)
		go addFileToZip(&wg, &mutex, zipWriter, path)

		return nil
	})

	if err != nil {
		fmt.Printf("Failed to walk through image directory: %v\n", err)
		return
	}

	wg.Wait()

	fmt.Println("All images have been successfully archived.")
}

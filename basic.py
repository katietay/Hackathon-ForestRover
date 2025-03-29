import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tifffile
from matplotlib.path import Path
import matplotlib.patches as patches

def load_tiff(file_path, library="PIL"):
    """
    Load a TIFF file using either PIL or tifffile.
    Returns the TIFF data as a numpy array or list of arrays.
    
    Args:
        file_path: Path to the TIFF file
        library: Either "PIL" or "tifffile" to choose the loading method
    """
    try:
        if library.lower() == "pil":
            # Using PIL/Pillow
            with Image.open(file_path) as img:
                # Check if multi-page
                pages = []
                try:
                    img.seek(0)
                    while True:
                        pages.append(np.array(img))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass  # End of file, stop reading
                
                if len(pages) == 1:
                    return pages[0]  # Single page
                return pages  # Multi-page
        else:
            # Using tifffile
            return tifffile.imread(file_path)
            
        print(f"Successfully loaded: {file_path}")
    except Exception as e:
        print(f"Error loading TIFF file: {e}")
        return None

def display_tiff_info(tiff_data):
    """
    Display basic information about the loaded TIFF data.
    """
    if tiff_data is None:
        return
        
    if isinstance(tiff_data, list):
        print(f"Multi-page TIFF with {len(tiff_data)} pages")
        for i, page in enumerate(tiff_data):
            print(f"  Page {i}: Shape={page.shape}, Type={page.dtype}")
    else:
        print(f"Single-page TIFF: Shape={tiff_data.shape}, Type={tiff_data.dtype}")

def process_tiff(tiff_data, callback=None):
    """
    Process a TIFF file or its pages using the provided callback function.
    If no callback is provided, this will just traverse the data.
    """
    if tiff_data is None:
        return

    results = []
    
    # Handle both single and multi-page TIFFs
    if isinstance(tiff_data, list):
        for page_index, page in enumerate(tiff_data):
            print(f"Processing page {page_index}...")
            result = traverse_tiff_page(page, page_index, callback)
            results.append(result)
    else:
        # Single page TIFF
        result = traverse_tiff_page(tiff_data, 0, callback)
        results.append(result)
        
    return results

def traverse_tiff_page(page_data, page_index=0, callback=None):
    """
    Traverse a single TIFF page.
    If a callback is provided, apply it to each pixel or the whole page.
    """
    height, width = page_data.shape[:2]
    
    # If a callback function is provided, use it
    if callback and callable(callback):
        return callback(page_data, page_index)
    
    # Default behavior: just count non-zero pixels
    non_zero_count = np.count_nonzero(page_data)
    print(f"Page {page_index}: {non_zero_count} non-zero pixels out of {height*width} total")
    
    return {
        'page': page_index,
        'shape': page_data.shape,
        'dtype': str(page_data.dtype),
        'non_zero_count': non_zero_count,
        'min': np.min(page_data),
        'max': np.max(page_data),
        'mean': np.mean(page_data)
    }

def visualize_tiff_page(page_data, page_index=0):
    """
    Visualize a TIFF page using matplotlib.
    """
    plt.figure(figsize=(10, 8))
    
    # Handle different channel configurations
    if len(page_data.shape) == 3 and page_data.shape[2] in [3, 4]:
        # RGB or RGBA image
        plt.imshow(page_data)
    else:
        # Grayscale or other format
        plt.imshow(page_data, cmap='viridis')
        plt.colorbar(label='Pixel Value')
    
    plt.title(f'TIFF Page {page_index}')
    plt.show()

# Example custom callback function
def find_regions_of_interest(page_data, page_index):
    """
    Example callback that finds regions with values above a threshold.
    """
    # Ensure we're working with a 2D array if it's RGB/RGBA
    if len(page_data.shape) == 3:
        # Convert to grayscale if it's an RGB/RGBA image
        if page_data.shape[2] in [3, 4]:
            grayscale = np.mean(page_data[:,:,:3], axis=2)  # Average RGB channels
        else:
            grayscale = page_data[:,:,0]  # Use first channel
    else:
        grayscale = page_data
    
    threshold = np.percentile(grayscale, 90)  # Use top 10% as threshold
    high_value_mask = grayscale > threshold
    regions = np.where(high_value_mask)
    
    print(f"Page {page_index}: Found {len(regions[0])} pixels above threshold {threshold:.2f}")
    
    return {
        'page': page_index,
        'threshold': threshold,
        'high_value_pixels': len(regions[0]),
        'regions': regions
    }

def extract_path_from_image(image_data, threshold=None, percentile=90):
    """
    Extract a path from an image by following pixels above a threshold.
    
    Args:
        image_data: NumPy array of image
        threshold: Explicit pixel value threshold (if None, use percentile)
        percentile: Percentile to use for threshold if threshold is None
        
    Returns:
        List of (x, y) coordinates representing the path
    """
    # Ensure we're working with a 2D array if it's RGB/RGBA
    if len(image_data.shape) == 3:
        if image_data.shape[2] in [3, 4]:
            gray_image = np.mean(image_data[:,:,:3], axis=2)  # Average RGB channels
        else:
            gray_image = image_data[:,:,0]  # Use first channel
    else:
        gray_image = image_data
    
    # Determine threshold value
    if threshold is None:
        threshold = np.percentile(gray_image, percentile)
        print(f"Using threshold value: {threshold} (at {percentile}th percentile)")
    
    # Find pixels above threshold
    mask = gray_image > threshold
    path_pixels = np.where(mask)
    
    # Convert to list of coordinates
    coordinates = list(zip(path_pixels[1], path_pixels[0]))  # Note: x=column, y=row
    
    if not coordinates:
        print("No pixels above threshold found.")
        return []
    
    print(f"Found {len(coordinates)} pixels above threshold {threshold}")
    
    # Sort coordinates to create a continuous path
    sorted_coords = [coordinates[0]]
    remaining = set(coordinates)
    remaining.remove(coordinates[0])
    
    while remaining:
        current = sorted_coords[-1]
        # Find the closest remaining point
        closest = min(remaining, key=lambda p: (p[0]-current[0])**2 + (p[1]-current[1])**2)
        
        # Check if distance is too large (disconnected path)
        dist = (closest[0]-current[0])**2 + (closest[1]-current[1])**2
        if dist > 100:
            print(f"Path gap detected (distance: {np.sqrt(dist):.2f} pixels). Starting new path segment.")
            # Optionally, we could start a new path segment here
        
        sorted_coords.append(closest)
        remaining.remove(closest)
        
        # Progress indicator for large paths
        if len(sorted_coords) % 1000 == 0:
            print(f"Path construction: {len(sorted_coords)}/{len(coordinates)} points processed")
    
    print(f"Path created with {len(sorted_coords)} points")
    return sorted_coords

def visualize_path(image_data, path_coords, title="Image with Extracted Path"):
    """
    Visualize the image with the extracted path overlaid.
    
    Args:
        image_data: The original image as a NumPy array
        path_coords: List of (x, y) coordinates representing the path
        title: Title for the plot
    """
    plt.figure(figsize=(12, 10))
    
    # Display the image
    if len(image_data.shape) == 3:
        plt.imshow(image_data)
    else:
        plt.imshow(image_data, cmap='viridis')
    
    # Create a matplotlib path
    if path_coords:
        # Draw the path
        x_coords = [p[0] for p in path_coords]
        y_coords = [p[1] for p in path_coords]
        plt.plot(x_coords, y_coords, 'r-', linewidth=1, alpha=0.7)
        
        # Plot start and end points
        plt.plot(path_coords[0][0], path_coords[0][1], 'go', markersize=10)  # Start
        plt.plot(path_coords[-1][0], path_coords[-1][1], 'bo', markersize=10)  # End
        
        # Add legend
        plt.plot([], [], 'r-', label='Path')
        plt.plot([], [], 'go', label='Start')
        plt.plot([], [], 'bo', label='End')
        plt.legend()
    else:
        plt.title(f"{title} (No path found)")
        return
    
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
    # Also show a path-only view for clarity
    plt.figure(figsize=(12, 10))
    plt.plot(x_coords, y_coords, 'r-', linewidth=2)
    plt.plot(path_coords[0][0], path_coords[0][1], 'go', markersize=10)  # Start
    plt.plot(path_coords[-1][0], path_coords[-1][1], 'bo', markersize=10)  # End
    plt.title(f"{title} - Path Only")
    plt.grid(True)
    plt.legend(['Path', 'Start', 'End'])
    plt.tight_layout()
    plt.show()

def extract_and_visualize_path(tiff_data, threshold=3000, percentile=90):
    """
    Extract a path from TIFF data and visualize it.
    Handles both single and multi-page TIFFs.
    
    Args:
        tiff_data: TIFF data (single array or list of arrays)
        threshold: Explicit threshold value (if None, use percentile)
        percentile: Percentile to use for threshold if threshold is None
        
    Returns:
        Dictionary with paths for each page
    """
    results = {}
    
    # Handle both single and multi-page TIFFs
    if isinstance(tiff_data, list):
        for page_index, page in enumerate(tiff_data):
            print(f"\nProcessing page {page_index} for path extraction...")
            path = extract_path_from_image(page, threshold, percentile)
            visualize_path(page, path, f"TIFF Page {page_index} with Path")
            results[f"page_{page_index}"] = path
    else:
        # Single page TIFF
        print("\nProcessing single-page TIFF for path extraction...")
        path = extract_path_from_image(tiff_data, threshold, percentile)
        visualize_path(tiff_data, path, "TIFF with Path")
        results["single_page"] = path
    
    return results

def save_path_to_file(path_coords, output_file):
    """
    Save path coordinates to a file.
    
    Args:
        path_coords: List of (x, y) coordinates
        output_file: File path to save to
    """
    try:
        with open(output_file, 'w') as f:
            f.write("x,y\n")  # Header
            for x, y in path_coords:
                f.write(f"{x},{y}\n")
        print(f"Path saved to {output_file}")
    except Exception as e:
        print(f"Error saving path to file: {e}")

# Main function to demonstrate usage
def main():
    # Replace with your TIFF file path
    file_path = "starter_code_nasa\masked_output_chunk_4096_4608.tiff"
    
    # Load the TIFF file (using PIL by default, can change to "tifffile")
    tiff_data = load_tiff(file_path, library="PIL")
    if tiff_data is None:
        return
    
    # Display information about the TIFF
    display_tiff_info(tiff_data)
    
    # Process the TIFF (basic traversal)
    results = process_tiff(tiff_data)
    print(results)
    
    # Process with custom callback
    custom_results = process_tiff(tiff_data, find_regions_of_interest)
    print(custom_results)
    
    # Visualize the first page (if it's a multi-page TIFF)
    if isinstance(tiff_data, list) and len(tiff_data) > 0:
        visualize_tiff_page(tiff_data[0], 0)
    elif not isinstance(tiff_data, list):
        visualize_tiff_page(tiff_data, 0)
    
    # Extract and visualize a path (using the top 10% brightest pixels)
    path_results = extract_and_visualize_path(tiff_data, percentile=90)
    # Save the first path to a CSV file
    if path_results:
        first_path_key = list(path_results.keys())[0]
        first_path = path_results[first_path_key]
        if first_path:
            save_path_to_file(first_path, "extracted_path.csv")

if __name__ == "__main__":
    main()
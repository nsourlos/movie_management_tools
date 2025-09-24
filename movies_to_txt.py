import os
import re

def extract_movie_names(folder_path, output_file="movies.txt"):
    """
    Extract movie names from folder names in a directory and save them to a txt file.
    Movie names are extracted from before parentheses containing bluray/dvd info.
    """
    movie_names = []
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    # Get all folders in the directory
    try:
        items = os.listdir(folder_path)
    except PermissionError:
        print(f"Error: Permission denied to access folder '{folder_path}'.")
        return
    
    # Pattern to match movie names before parentheses with bluray/dvd info
    pattern = r'^(.+?)\s*\([^)]*(?:bluray|dvd|blu-ray|rip)[^)]*\)'
    
    for item_name in items:
        # Only process directories
        item_path = os.path.join(folder_path, item_name)
        if not os.path.isdir(item_path):
            continue
        
        # Skip movies with 'of10' in their name
        if 'of10' in item_name.lower():
            continue
            
        # Extract movie name using regex (case insensitive)
        match = re.search(pattern, item_name, re.IGNORECASE)
        if match:
            movie_name = match.group(1).strip()
            if movie_name and movie_name not in movie_names:
                movie_names.append(movie_name)
    
    # Sort movie names alphabetically
    movie_names.sort()
    
    # Save to txt file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for movie in movie_names:
                f.write(movie + '\n')
        
        print(f"Successfully extracted {len(movie_names)} movie names to '{output_file}'")
        print("Movies found:")
        # for movie in movie_names:
        #     print(f"  - {movie}")
            
    except Exception as e:
        print(f"Error writing to file: {e}")

# Main execution
if __name__ == "__main__":
    folder_path = r"G:\folder_name\Movies"
    extract_movie_names(folder_path)
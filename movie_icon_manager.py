import os
import re
import requests
import json
from PIL import Image
import ctypes
from ctypes import wintypes, windll
import time
from urllib.parse import quote_plus
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MovieIconManager:
    def __init__(self, movies_folder_path, icons_folder="movie_icons"):
        self.movies_folder_path = movies_folder_path
        self.icons_folder = icons_folder
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create icons folder if it doesn't exist
        if not os.path.exists(self.icons_folder):
            os.makedirs(self.icons_folder)
    
    def extract_movie_names(self):
        """
        Extract movie names from folder names, handling both '(Bluray' and '- nof10' patterns.
        """
        movie_data = []
        
        if not os.path.exists(self.movies_folder_path):
            logger.error(f"Folder '{self.movies_folder_path}' does not exist.")
            return movie_data
        
        try:
            items = os.listdir(self.movies_folder_path)
        except PermissionError:
            logger.error(f"Permission denied to access folder '{self.movies_folder_path}'.")
            return movie_data
        
        for item_name in items:
            item_path = os.path.join(self.movies_folder_path, item_name)
            if not os.path.isdir(item_path):
                continue
            
            original_name = item_name
            movie_name = self._extract_clean_name(item_name)
            
            if movie_name:
                movie_data.append({
                    'original_folder_name': original_name,
                    'clean_name': movie_name,
                    'folder_path': item_path
                })
                logger.info(f"Extracted: '{movie_name}' from '{original_name}'")
        
        logger.info(f"Successfully extracted {len(movie_data)} movie names")
        return movie_data
    
    def _extract_clean_name(self, folder_name):
        """
        Extract clean movie name from folder name.
        Handles patterns like '(Bluray', '(BluRay', '- nof10', etc.
        """
        # Pattern for Bluray/DVD info in parentheses
        bluray_pattern = r'^(.+?)\s*\([^)]*(?:bluray|blu-ray|dvd|rip|)[^)]*\)'
        
        # Pattern for rating format '- nof10'
        rating_pattern = r'^(.+?)\s*-\s*\d+of10.*'
        
        # Try bluray pattern first
        match = re.search(bluray_pattern, folder_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try rating pattern
        match = re.search(rating_pattern, folder_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # If no pattern matches, return the original name (cleaned)
        return folder_name.strip()
    
    def search_imdb_poster(self, movie_name):
        """
        Search for movie poster on IMDb using web scraping.
        Returns the poster URL if found.
        """
        try:
            # Search IMDb
            search_url = f"https://www.imdb.com/find?q={quote_plus(movie_name)}&s=tt&ttype=ft"
            logger.info(f"Searching IMDb for: {movie_name}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Look for the first movie result
            content = response.text
            
            # Find the first movie link
            movie_link_pattern = r'/title/(tt\d+)/'
            match = re.search(movie_link_pattern, content)
            
            if not match:
                logger.warning(f"No movie found for: {movie_name}")
                return None
            
            movie_id = match.group(1)
            movie_url = f"https://www.imdb.com/title/{movie_id}/"
            
            # Get the movie page
            movie_response = self.session.get(movie_url, timeout=10)
            movie_response.raise_for_status()
            
            movie_content = movie_response.text
            
            # Find poster image URL
            poster_patterns = [
                r'<img[^>]*class="[^"]*ipc-image[^"]*"[^>]*src="([^"]+)"',
                r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*ipc-image[^"]*"',
                r'property="og:image"[^>]*content="([^"]+)"'
            ]
            
            for pattern in poster_patterns:
                matches = re.findall(pattern, movie_content)
                for match in matches:
                    if 'amazon' in match and ('jpg' in match or 'jpeg' in match):
                        # Clean up the URL (remove resize parameters for better quality)
                        clean_url = re.sub(r'_V1_.*?\.(jpg|jpeg)', r'_V1_SX300.\1', match)
                        logger.info(f"Found poster for {movie_name}: {clean_url}")
                        return clean_url
            
            logger.warning(f"No poster found for: {movie_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for {movie_name}: {e}")
            return None
    
    def download_image(self, url, filename):
        """
        Download image from URL and save to file.
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return False
    
    def convert_to_icon(self, image_path, icon_path):
        """
        Convert image to .ico format with multiple sizes.
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create multiple sizes for the icon
                sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
                icon_images = []
                
                for size in sizes:
                    resized = img.resize(size, Image.LANCZOS)
                    icon_images.append(resized)
                
                # Save as ICO
                icon_images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images])
                
            logger.info(f"Converted to icon: {icon_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting {image_path} to icon: {e}")
            return False
    
    def set_folder_icon(self, folder_path, icon_path):
        """
        Set custom icon for Windows folder.
        """
        try:
            # Create desktop.ini content
            desktop_ini_content = f"""[.ShellClassInfo]
IconResource={os.path.abspath(icon_path)},0
[ViewState]
Mode=
Vid=
FolderType=Generic
"""
            
            desktop_ini_path = os.path.join(folder_path, 'desktop.ini')
            
            # Write desktop.ini file
            with open(desktop_ini_path, 'w', encoding='utf-8') as f:
                f.write(desktop_ini_content)
            
            # Set file attributes (hidden and system)
            FILE_ATTRIBUTE_HIDDEN = 0x02
            FILE_ATTRIBUTE_SYSTEM = 0x04
            
            ctypes.windll.kernel32.SetFileAttributesW(desktop_ini_path, 
                                                    FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
            
            # Set folder as system folder to enable custom icon
            ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_SYSTEM)
            
            # Refresh the folder to show new icon
            SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
            SHCNE_ASSOCCHANGED = 0x08000000
            SHCNF_IDLIST = 0x0000
            SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
            
            logger.info(f"Set icon for folder: {folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting icon for {folder_path}: {e}")
            return False
    
    def process_all_movies(self):
        """
        Main method to process all movies: extract names, download posters, convert to icons, and set folder icons.
        """
        logger.info("Starting movie icon processing...")
        
        # Extract movie names
        movies = self.extract_movie_names()
        if not movies:
            logger.error("No movies found to process")
            return
        
        success_count = 0
        
        for movie in movies:
            movie_name = movie['clean_name']
            folder_path = movie['folder_path']
            
            logger.info(f"Processing: {movie_name}")
            
            # Search for poster
            poster_url = self.search_imdb_poster(movie_name)
            if not poster_url:
                continue
            
            # Generate file names
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', movie_name)
            image_filename = os.path.join(self.icons_folder, f"{safe_name}.jpg")
            icon_filename = os.path.join(self.icons_folder, f"{safe_name}.ico")
            
            # Download image
            if not self.download_image(poster_url, image_filename):
                continue
            
            # Convert to icon
            if not self.convert_to_icon(image_filename, icon_filename):
                continue
            
            # Set folder icon
            if self.set_folder_icon(folder_path, icon_filename):
                success_count += 1
            
            # Add delay to be respectful to IMDb
            time.sleep(1)
        
        logger.info(f"Successfully processed {success_count} out of {len(movies)} movies")

def main():
    # Configuration
    # MOVIES_FOLDER = input("Enter the path to your movies folder: ").strip()
    MOVIES_FOLDER = r"G:\folder_name\Movies"
    
    # if not MOVIES_FOLDER:
    #     MOVIES_FOLDER = r"G:\folder_name\Movies"  # Default from your existing script
    
    # Create manager and process movies
    manager = MovieIconManager(MOVIES_FOLDER)
    manager.process_all_movies()

if __name__ == "__main__":
    main()

# Movie Management Tools

A collection of Python scripts for managing movie folders and automatically setting custom icons by downloading movie posters from IMDb.

## Scripts Included

### 1. Movie Icon Manager (`movie_icon_manager.py`)
Automatically sets custom icons for movie folders by downloading movie posters from IMDb and converting them to Windows folder icons.

### 2. Movies to Text (`movies_to_txt.py`)
Extracts clean movie names from folder names and saves them to a text file for easy reference.

## Features

### Movie Icon Manager
- Extracts clean movie names from folder names with various formats:
  - Folders with `(Bluray)`, `(BluRay)`, `(DVD)` etc.
  - Folders with ratings like `- 8of10`
- Searches IMDb for movie posters
- Downloads high-quality poster images
- Converts images to Windows icon format (.ico)
- Automatically sets folder icons on Windows

### Movies to Text
- Scans movie folders and extracts clean movie names
- Filters out folders with rating patterns (e.g., `of10`)
- Saves alphabetically sorted movie list to `movies.txt`
- Handles various folder naming conventions

## Requirements

- Windows operating system (for icon setting functionality)
- Python 3.7+
- Required packages (install via `pip install -r requirements.txt`):
  - requests
  - Pillow

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Movie Icon Manager

1. Run the script:
   ```bash
   python movie_icon_manager.py
   ```

2. The script will use the configured movies folder path (edit the `MOVIES_FOLDER` variable in the script)

3. The script will:
   - Scan all folders in the specified directory
   - Extract clean movie names
   - Search IMDb for each movie
   - Download poster images
   - Convert them to icon format
   - Set the folder icons

### Movies to Text

1. Run the script:
   ```bash
   python movies_to_txt.py
   ```

2. The script will:
   - Scan the configured movies folder
   - Extract clean movie names from folder names
   - Save the sorted list to `movies.txt`

## Example Folder Names

Both scripts can handle various folder naming conventions:

- `The Matrix (1999) (Bluray)` → `The Matrix`
- `Inception - 9of10` → `Inception`
- `Pulp Fiction (BluRay)` → `Pulp Fiction`
- `Fight Club (DVD Rip)` → `Fight Club`

## Output

### Movie Icon Manager
- Downloaded images and icons are saved in the `movie_icons` folder
- Each folder gets a `desktop.ini` file to display the custom icon
- Progress and errors are logged to the console

### Movies to Text
- Creates `movies.txt` with alphabetically sorted movie names
- One movie name per line
- Skips folders with rating patterns

## Configuration

Both scripts have configurable folder paths at the top of their respective files:

- **Movie Icon Manager**: Edit the `MOVIES_FOLDER` variable in `main()` function
- **Movies to Text**: Edit the `folder_path` variable at the bottom of the script

## Notes

- The Movie Icon Manager adds a 1-second delay between requests to be respectful to IMDb
- Some movies might not be found on IMDb or might not have poster images
- Administrator privileges might be required for setting folder attributes
- Icons will appear after refreshing the folder view (F5)
- Movies to Text skips folders containing 'of10' to avoid rating-based duplicates

## Troubleshooting

If folder icons don't appear immediately:
1. Press F5 to refresh the folder view
2. Close and reopen File Explorer
3. Check that the `desktop.ini` file was created in the folder
4. Ensure you have write permissions to the movie folders

If movies aren't being extracted properly:
1. Check the folder path configuration
2. Ensure folder names follow supported patterns
3. Verify read permissions for the movies directory
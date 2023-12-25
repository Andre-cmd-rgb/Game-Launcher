import ctypes
import logging
import os
import requests
import tempfile
import zipfile
import time
from PIL import Image, ImageTk  # Import Pillow for working with images
import tkinter as tk
from tkinter import messagebox

# Constants
OWNER = "Andre-cmd-rgb"
REPO = "Game Launcher"
ASSET_NAME = "FuryOfSnipersRevenge.zip"
TARGET_DIR = r"C:\Program Files\Game Launcher\Game\FuryOfSnipers"



# Check for admin privileges
if not ctypes.windll.shell32.IsUserAnAdmin():
    print('Not enough privilege, restarting...')
    import sys
    ctypes.windll.shell32.ShellExecuteW(
        None, 'runas', sys.executable, ' '.join(sys.argv), None, None)
    sys.exit()
else:
    print('Elevated privilege acquired')


# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Check for installed version
version_file_path = os.path.join(TARGET_DIR, "version.txt")
if os.path.isfile(version_file_path):
    with open(version_file_path, "r") as version_file:
        installed_version = version_file.read().strip()

def download_and_extract_github_release(owner, repo, asset_name, target_dir):
    # Define the GitHub API URL for the releases of the repository
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    try:
        # Send a GET request to the GitHub API
        response = requests.get(api_url)
        response.raise_for_status()

        # Parse the JSON response to get the release information
        release_info = response.json()

        # Find the asset with the specified name 
        asset = next((a for a in release_info['assets'] if a['name'] == asset_name), None)

        if asset:
            # Get the download URL of the asset
            download_url = asset['browser_download_url']

            # Create a temporary directory to store the downloaded file
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download the asset
                response = requests.get(download_url)
                response.raise_for_status()

                # Define the path to save the downloaded file
                download_path = os.path.join(temp_dir, asset_name)

                # Save the downloaded file
                with open(download_path, 'wb') as file:
                    file.write(response.content)

                # Extract the downloaded file (assuming it's a ZIP file)
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)

            logging.info(f"Downloaded and extracted {asset_name} successfully to {target_dir}")
        else:
            logging.info(f"Asset '{asset_name}' not found in the latest release")

    except requests.exceptions.RequestException as e:
        logging.info(f"Error: {e}")

def is_newest_version_installed(owner, repo, asset_name, installed_version):
    # Define the GitHub API URL for the releases of the repository
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    try:
        # Send a GET request to the GitHub API
        response = requests.get(api_url)
        response.raise_for_status()

        # Parse the JSON response to get the release information
        release_info = response.json()

        # Get the tag name (version) of the latest release
        latest_version = release_info['tag_name']

        # Compare the installed version with the latest version
        if latest_version == installed_version:
            logging.info(f"The newest version ({latest_version}) is already installed.")
            return True
        else:
            logging.info(f"A newer version ({latest_version}) is available.")
            return False

    except requests.exceptions.RequestException as e:
        logging.info(f"Error: {e}")
        return False

def launch_game():
    logging.info('Checking if the newest version is installed...')
    if not is_newest_version_installed(OWNER, REPO, ASSET_NAME, installed_version):
        logging.info('Newest version not installed. Downloading and extracting...')
        download_and_extract_github_release(OWNER, REPO, ASSET_NAME, TARGET_DIR)
    logging.info('Launching game...')
    os.system(r'"C:\Program Files\Game Launcher\Game\fly1-test.exe"')


def update_launch_button():
    if is_newest_version_installed(OWNER, REPO, ASSET_NAME, installed_version):
        launch_button.config(text="Launch", state=tk.NORMAL)
    else:
        launch_button.config(text="Update", state=tk.NORMAL)

def create_round_button(parent, radius, text, command):
    button = tk.Button(parent, text=text, width=6*radius, height=radius, relief="flat", bg="white", fg="black", command=command)
    button.place(relx=0.5, rely=0.5, anchor="center")
    return button

# Create the main window
root = tk.Tk()
root.title("Game Launcher")
window_width = 1200
window_height = 800
root.geometry(f"{window_width}x{window_height}")
root.resizable(False, False)

# Load the background image
bg_image = Image.open(r"C:\Program Files\Game Launcher\assets\background.png")
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Create a frame to center the button
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Create a round button for launching or updating
launch_button = create_round_button(frame, 1, "Checking for updates...", launch_game)
launch_button.pack()  # Pack the button within the frame

# Update the button label during app startup
update_launch_button()


root.mainloop()

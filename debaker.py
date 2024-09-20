import zipfile
import os
import tkinter as tk
from tkinter import filedialog

def read_default_file_list(file_path):
    """Read the list of default files from a .txt file."""
    with open(file_path, 'r') as file:
        default_files = [line.strip() for line in file if line.strip()]
    return default_files

def delete_files_from_zip(zip_file_path, files_to_delete):
    """Delete specified files from the .zip archive."""
    temp_zip_path = zip_file_path + ".temp"
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        with zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
            # Write files that are not in the files_to_delete list to the temp zip
            for item in zip_file.infolist():
                if item.filename not in files_to_delete:
                    temp_zip.writestr(item, zip_file.read(item.filename))
    
    # Replace original zip file with the temp zip file
    os.replace(temp_zip_path, zip_file_path)

def find_associated_model_files(zip_set, model_file):
    """Find associated model files that share the same base name as the .mdl file."""
    base_name = os.path.splitext(model_file)[0]  # Get the base file name without extension
    associated_extensions = ['.dx80.vtx', '.dx90.vtx', '.phy', '.sw.vtx', '.vtx', '.vvd']
    
    associated_files = [
        f"{base_name}{ext}" for ext in associated_extensions if f"{base_name}{ext}" in zip_set
    ]
    
    # Include the original .mdl file
    associated_files.append(model_file)
    
    return associated_files

def compare_zip_with_list(zip_file_path, default_textures_file, default_models_file, default_sounds_file):
    """Compare the .zip file's contents with the default textures, models, and sounds lists."""
    try:
        # Read the default textures and sounds from their respective .txt files
        default_textures_list = read_default_file_list(default_textures_file)
        default_models_list = read_default_file_list(default_models_file)  # Read the .mdl files only
        default_sounds_list = read_default_file_list(default_sounds_file)

        # Read the contents of the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            zip_contents = zip_file.namelist()

        # Convert lists to sets for easier comparison
        textures_set = set(default_textures_list)
        sounds_set = set(default_sounds_list)
        zip_set = set(zip_contents)

        # Find files from textures and sounds that are found in the zip
        default_textures_found = sorted(textures_set.intersection(zip_set))
        default_sounds_found = sorted(sounds_set.intersection(zip_set))

        # For each .mdl file in the default list, find its associated files automatically
        default_models_found = []
        mdl_files_in_zip = set(f for f in zip_set if f.endswith('.mdl'))

        for mdl_file in mdl_files_in_zip.intersection(set(default_models_list)):
            associated_files = find_associated_model_files(zip_set, mdl_file)
            default_models_found.extend(associated_files)

        default_models_found = sorted(default_models_found)

        # Print results for textures
        if default_textures_found:
            print("Textures found in the default list (sorted):")
            for file in default_textures_found:
                print(f"- {file}")
        else:
            print("No textures from the default list found.")

        # Print results for models
        if default_models_found:
            print("\nModels and associated files found (sorted):")
            for file in default_models_found:
                print(f"- {file}")
        else:
            print("No models or associated files found.")

        # Print results for sounds
        if default_sounds_found:
            print("\nSounds found in the default list (sorted):")
            for file in default_sounds_found:
                print(f"- {file}")
        else:
            print("No sounds from the default list found.")

        # Ask user if they want to delete the matching files
        if default_textures_found or default_models_found or default_sounds_found:
            user_input = input("\nDo you want to delete the matching files from the zip archive? (yes/no): ").strip().lower()
            if user_input == 'yes':
                files_to_delete = default_textures_found + default_models_found + default_sounds_found
                delete_files_from_zip(zip_file_path, files_to_delete)
                print("\nThe matching files have been deleted from the zip archive.")
            else:
                print("\nNo files were deleted.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the specified paths for the .txt files are correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def browse_for_zip_file():
    """Open a file dialog to allow the user to select a .zip file."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    zip_file_path = filedialog.askopenfilename(
        title="Select Zip File",
        filetypes=[("Zip Files", "*.zip")]
    )
    return zip_file_path

# Example usage
default_textures_file = 'path/to/your/default_textures.txt'  # Path to your .txt file containing the list of default textures
default_models_file = 'path/to/your/default_models.txt'  # Path to your .txt file containing the list of default .mdl files
default_sounds_file = 'path/to/your/default_sounds.txt'  # Path to your .txt file containing the list of default sounds

# Browse for the zip file
zip_file_path = browse_for_zip_file()

if zip_file_path:
    compare_zip_with_list(zip_file_path, default_textures_file, default_models_file, default_sounds_file)
else:
    print("No zip file was selected.")

# Wait for the user to press any key before exiting using os.system('pause')
os.system('pause')

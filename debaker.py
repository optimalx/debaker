import zipfile
import os
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog

# Function to read the default file list from a .txt file
def read_default_file_list(file_path):
    with open(file_path, 'r') as file:
        default_files = [line.strip() for line in file if line.strip()]
    return default_files

# Function to delete specified files from a zip archive
def delete_files_from_zip(zip_file_path, files_to_delete):
    temp_zip_path = zip_file_path + ".temp"
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        with zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
            # Write files that are not in the files_to_delete list to the temp zip
            for item in zip_file.infolist():
                if item.filename not in files_to_delete:
                    temp_zip.writestr(item, zip_file.read(item.filename))
    
    # Replace original zip file with the temp zip file
    os.replace(temp_zip_path, zip_file_path)

# Function to find associated model files that share the same base name as the .mdl file
def find_associated_model_files(zip_set, model_file):
    base_name = os.path.splitext(model_file)[0]
    associated_extensions = ['.dx80.vtx', '.dx90.vtx', '.phy', '.sw.vtx', '.vtx', '.vvd']
    
    associated_files = [f"{base_name}{ext}" for ext in associated_extensions if f"{base_name}{ext}" in zip_set]
    associated_files.append(model_file)
    
    return associated_files

# Function to find *.xbox.vtx and *.sw.vtx files
def find_vtx_files(zip_path):
    xbox_vtx_files = []
    sw_vtx_files = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.xbox.vtx'):
                xbox_vtx_files.append((file_info.filename, file_info.file_size))
            elif file_info.filename.endswith('.sw.vtx'):
                sw_vtx_files.append((file_info.filename, file_info.file_size))
    
    return xbox_vtx_files, sw_vtx_files

# Helper function to convert bytes to a human-readable format
def format_file_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

# Function to remove empty folders after file deletion
def remove_empty_folders(path):
    if os.path.isdir(path):
        for root, dirs, _ in os.walk(path, topdown=False):
            for dir_ in dirs:
                dir_path = os.path.join(root, dir_)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

# Function to print the VTX files and handle user deletion
def prompt_user_for_vtx_deletion(file_list, zip_path):
    if not file_list:
        return

    file_list.sort()
    total_size = sum(size for _, size in file_list)

    print(f"\nFound {len(file_list)} VTX file(s):")
    for file, size in file_list:
        print(f" - {file} ({format_file_size(size)})")
    
    print(f"\nTotal size of found VTX files: {format_file_size(total_size)}")

    delete = input("\nWould you like to delete these VTX files? (yes/no): ").lower()

    if delete == 'yes':
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for file, _ in file_list:
                file_path = os.path.join(temp_dir, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    parent_dir = os.path.dirname(file_path)
                    remove_empty_folders(parent_dir)

            with zipfile.ZipFile(zip_path, 'w') as new_zip_ref:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, temp_dir)
                        new_zip_ref.write(full_path, rel_path)

            print(f"\nOriginal zip file has been updated: {zip_path}")

# Main comparison function for textures, models, and sounds
def compare_zip_with_list(zip_file_path, default_textures_file, default_models_file, default_sounds_file):
    try:
        default_textures_list = read_default_file_list(default_textures_file)
        default_models_list = read_default_file_list(default_models_file)
        default_sounds_list = read_default_file_list(default_sounds_file)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            zip_contents = zip_file.namelist()

        textures_set = set(default_textures_list)
        sounds_set = set(default_sounds_list)
        zip_set = set(zip_contents)

        default_textures_found = sorted(textures_set.intersection(zip_set))
        default_sounds_found = sorted(sounds_set.intersection(zip_set))

        default_models_found = []
        mdl_files_in_zip = set(f for f in zip_set if f.endswith('.mdl'))

        for mdl_file in mdl_files_in_zip.intersection(set(default_models_list)):
            associated_files = find_associated_model_files(zip_set, mdl_file)
            default_models_found.extend(associated_files)

        default_models_found = sorted(default_models_found)

        if not default_textures_found and not default_models_found and not default_sounds_found:
            print("No matching textures, models, or sounds from the default list were found in the zip.")
        else:
            if default_textures_found:
                print("Textures found:")
                for file in default_textures_found:
                    print(f"- {file}")
            if default_models_found:
                print("\nModels found:")
                for file in default_models_found:
                    print(f"- {file}")
            if default_sounds_found:
                print("\nSounds found:")
                for file in default_sounds_found:
                    print(f"- {file}")

            user_input = input("\nDo you want to delete the matching files? (yes/no): ").strip().lower()
            if user_input == 'yes':
                files_to_delete = default_textures_found + default_models_found + default_sounds_found
                delete_files_from_zip(zip_file_path, files_to_delete)
                print("\nMatching files deleted.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the paths are correct.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Browse for zip file function
def browse_for_zip_file():
    root = tk.Tk()
    root.withdraw()
    zip_file_path = filedialog.askopenfilename(
        title="Select Zip File",
        filetypes=[("Zip Files", "*.zip")]
    )
    return zip_file_path

def main():
    default_textures_file = 'F:/Source Engine/Mapping/tools/optimizer/default_textures.txt'
    default_models_file = 'F:/Source Engine/Mapping/tools/optimizer/default_models.txt'
    default_sounds_file = 'F:/Source Engine/Mapping/tools/optimizer/default_sounds.txt'

    zip_file_path = browse_for_zip_file()

    if zip_file_path:
        compare_zip_with_list(zip_file_path, default_textures_file, default_models_file, default_sounds_file)
        xbox_vtx_files, sw_vtx_files = find_vtx_files(zip_file_path)
        if not xbox_vtx_files and not sw_vtx_files:
            print("No *.xbox.vtx or *.sw.vtx files were found.")
        else:
            prompt_user_for_vtx_deletion(xbox_vtx_files + sw_vtx_files, zip_file_path)
    else:
        print("No zip file selected.")

    os.system('pause')

if __name__ == "__main__":
    main()

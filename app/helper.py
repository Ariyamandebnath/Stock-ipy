import os
import shutil

def delete_files_except_one(folder_path, file_to_keep):
    try:
        # Ensure the folder path ends with a slash
        if not folder_path.endswith(os.path.sep):
            folder_path += os.path.sep
        
        # Get a list of all files in the folder
        files = os.listdir(folder_path)
        
        # Iterate through all files
        for file in files:
            file_path = os.path.join(folder_path, file)
            
            # Check if the file is not the one you want to keep
            if file != file_to_keep:
                # Delete the file
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Recursively delete directories
            
        print(f"All files except '{file_to_keep}' deleted successfully.")
        
    except Exception as e:
        print(f"Error occurred: {e}")

# Example usage:
folder_path = '/path/to/your/folder'  # Replace with your folder path
file_to_keep = 'important_file.txt'  # Replace with the file you want to keep

delete_files_except_one(folder_path, file_to_keep)

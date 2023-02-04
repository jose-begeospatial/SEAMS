import os
import tempfile
import shutil
from PIL import Image
from typing import Dict, List



def read_photos(folder_path:str)->Dict[str, str | List]:
    """Read a folder path for JPG and PNG photos.

    Args:
        folder_path (str): _description_

    Raises:
        ValueError: _description_
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"{folder_path} is not a valid directory")
    photos = []
    folder_name = os.path.basename(folder_path)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            try:
                with open(os.path.join(folder_path, file_name), "rb") as f:
                    photos.append(f.read())
            except:
                raise IOError(f'Error opening file {file_name}')
    return {
        "folder_name": folder_name,
        "folder_path": folder_path,
        "photos": photos
         }



# --- tests

def test_read_photos():
    """Test for read_photos.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create a test JPG file
    test_jpg = Image.new("RGB", (100,100), "red")
    test_jpg_path = os.path.join(temp_dir, "test.jpg")
    test_jpg.save(test_jpg_path)

    # Create a test PNG file
    test_png = Image.new("RGB", (100,100), "green")
    test_png_path = os.path.join(temp_dir, "test.png")
    test_png.save(test_png_path)

    # Test reading valid photos

    result = read_photos(folder_path=temp_dir)
    assert len(result["photos"]) == 2
    assert result["folder_name"] == os.path.basename(temp_dir)
    assert result["folder_path"] == temp_dir 

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)
   
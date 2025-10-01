'''
Library of useful functions for working with images.
'''
import requests
import ctypes
import subprocess
import os
 
def main():
    image_url = 'https://apod.nasa.gov/apod/image/2304/PolarisIfn_Zayaz_4000.jpg'
    image_path = '/Users/Abdullah/Desktop/NGC3521LRGBHaAPOD-20.jpg'
    
    image_data = download_image(image_url)
    save_image_file(image_data, image_path)
    set_desktop_background_image(image_path)
    return

 
def download_image(image_url):
    """Downloads an image from a specified URL.
 
    DOES NOT SAVE THE IMAGE FILE TO DISK.
 
    Args:
        image_url (str): URL of image
 
    Returns:
        bytes: Binary image data, if succcessful. None, if unsuccessful.
    """
    # Send GET request to download the image
    print(f'Downloading image from {image_url}...', end='')
    resp_msg = requests.get(image_url)
 
    # Check if the image was retrieved successfully
    if resp_msg.status_code == requests.codes.ok:
        print('success')
        return resp_msg.content
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')     
 
def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.
 
    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file
 
    Returns:
        bool: True, if succcessful. False, if unsuccessful
    """
    try:
        print(f"Saving image file as {image_path}...", end='')
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print("success")
        return True
    except:
        print("failure")
        return False
 
def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.
 
    Args:
        image_path (str): Path of image file
 
    Returns:
        bool: True, if successful. False, if unsuccessful        
    """
    print(f"Setting desktop to {image_path}...", end='')
    
    # Check if the image file exists
    if not os.path.exists(image_path):
        print("failure - file not found")
        return False
    
    try:
        # Convert to absolute path and use POSIX format
        abs_path = os.path.abspath(image_path)
        
        # AppleScript to set desktop background for all desktops
        script = f'''tell application "Finder"
    set desktop picture to POSIX file "{abs_path}"
end tell'''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("success")
            return True
        else:
            print("failure")
            print(f"AppleScript error: {result.stderr}")
            return False
    except Exception as e:
        print("failure")
        print(f"Error: {e}")
        return False
 
def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  
 
    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).
 
    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size
 
if __name__ == '__main__':
    main()
'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''


import os
import requests


API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')  # Use DEMO_KEY as fallback
APOD_URL = 'https://api.nasa.gov/planetary/apod'

def main():
    
    apod_info = get_apod_info('2004-08-08')
    print(apod_info)
    image_url = get_apod_image_url(apod_info)
    print("Image URL:", image_url)
    
    
    return None

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.
    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)
    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    
   
    # Parameters for the APOD API call
    image_params = {
     'api_key': API_KEY, 
     'date': apod_date
    }
    
    # Makes a GET request to the APOD API using the specified parameters
    req = requests.get(APOD_URL, params=image_params)
    
    # If the API call is successful, returns the APOD info dictionary
    if req.status_code == 200:
        print(f'Getting {apod_date} APOD information from NASA...success')
        return req.json()
        
    # If the API call is unsuccessful, returns None
    if req.status_code > 200:
        print(f'failure to get APOD Information - Status: {req.status_code}')
        print(f'Error message: {req.text}')
        return None
    
   

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.
    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.
    Args:
        apod_info_dict (dict): Dictionary of APOD info from API
    Returns:
        str: APOD image URL
    """
    
    # Determines whether the APOD is an image or video
    media_type = apod_info_dict['media_type']
    
    # If the APOD is an image, gets the URL of the high definition image
    if media_type == 'image':
        image_url = apod_info_dict['hdurl'] 
        return image_url
    
    # If the APOD is a video, gets the URL of the video thumbnail
    if media_type == 'video':
        # Check if thumbnail_url exists, otherwise use the regular url
        if 'thumbnail_url' in apod_info_dict:
            image_url = apod_info_dict['thumbnail_url']
        else:
            print("No thumbnail available for video, using regular URL")
            image_url = apod_info_dict.get('url', None)
        return image_url
    
    # If the APOD is neither an image nor a video, prints a message to the console and returns None
    else:
        print('Invalid media type')
        return None
    
    
    
    


if __name__ == '__main__':
    main()
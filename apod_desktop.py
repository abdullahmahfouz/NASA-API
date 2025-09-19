""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import os
import image_lib
import inspect
import sys
import hashlib
import sqlite3
from apod_api import get_apod_image_url
import apod_api
import re


# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
   
    apod_date = get_apod_date()    
    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_info !=0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    
    
    min_date = date(1995,6,16)
    # checks if there are more than one command-line arguments
    if len(sys.argv) > 1:
         # tries to covert the agrs into a date 
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        # exception ERROR if  the format is incorrect 
        except ValueError:
            print(f"Error: Invalid date format: {sys.argv[1]}. PLEASE use this format (YYYY-MM-DD).")
            sys.exit(1)
    # if no date provided just uses today's date 
    else:
        apod_date = date.today()
    
    # if the date past 1995
    if apod_date < min_date:
        print(f"Error: Date {apod_date.isoformat()} is in past.")
        sys.exit(1)
        
     # if the date in the future 
    if apod_date > date.today():
        print(f"Error: Date {apod_date.isoformat()} is in the future.")
        sys.exit(1)
        
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    #  will store the paths to the image cache directory and database
    global image_cache_dir
    global image_cache_db
   # creates the path for the image cache directory joining the parent dircetory with the subdirectory  
    image_cache_dir = os.path.join(parent_dir, 'image_cache')
   #   checks if the image_cache_dir does not exist. If it doesn't, 
   # the directory is created using the os.makedirs() function.   
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print(f'Image cache directory: {image_cache_dir}')
        print('Image cache directory created.')
     # creates the path for the image cache database  by 
     # joining the image_cache_dir with the database file 
    else:
        print(f'Image cache directory: {image_cache_dir}')
        print('Image cache directory Already exists.')
     # creates the path for the image cache database  by 
     # joining the image_cache_dir with the database file 
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')
    # checks if the file does not already exist
    if not os.path.exists(image_cache_db) :
        # If the database file does not exist, creates a SQLite database by creating 
        # a new file named 'apod_cache.db' in the image Dir .
        con = sqlite3.connect(image_cache_db)
        # creats the new file named 'named 'apod_cache.db 
        cur = con.cursor()
       # create a new table named 'apod' in the database. 
        query = """
            CREATE TABLE IF NOT EXISTS image_apod
            (
               id    INTEGER PRIMARY KEY,
               title TEXT NOT NULL,
               explanation TEXT NOT NULL,
               file_path TEXT NOT NULL,
               sha256 TEXT NOT NULL 
            );
        """ 
        #  executes an SQL command for the database above
        cur.execute(query)
        # saving the changes made to the database
        con.commit()
        # closes the connection to the SQLite database
        con.close()
        print(f'Image cache DB Dir: {image_cache_db}')
        print('Image cache DB created.')
    else:
        
        print('Image cache DB Already exists')
        
def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    
    """
    
    # prints APOD date
    print("APOD date:", apod_date.isoformat())
    
    # gets the APOD date from APOD api
    apod_info = apod_api.get_apod_info(apod_date)
    
    # Extract the image explanation and title from the APOD information
    image_explantion = apod_info['explanation']
    image_title = apod_info['title']
    print(f'Image title: {image_title}')
   
    # gets the APOD image url
    apod_image_url = get_apod_image_url(apod_info)
    print(f'Image url:{apod_image_url}')
    
    # download the APOD image 
    image_data = image_lib.download_image(apod_image_url)
    
     # Calculate the hash of the downloaded image
    apod_hash = hashlib.sha256(image_data).hexdigest()
    print(f'APOD SHA-256:{apod_hash}')
    
     # Determine the file path for the APOD image
    APOD_path = determine_apod_file_path(image_title, apod_image_url)
    
    # Add the APOD information to the image cache database and get the APOD ID
    apod_id = add_apod_to_db(image_title, image_explantion, APOD_path, apod_hash)
   
    # Get the APOD ID from the cache using its  hash
    image = get_apod_id_from_db(apod_hash)
    
    # Save the APOD image file to the cache if it is not already present
    save_image =image_lib.save_image_file(image_data, APOD_path)
    
    # If the APOD image is not already in the cache, add it and save the image to the cache
    if image == 0:
        print('APOD image is not already in cache.')
        print('Adding image to cache')
        print(f'APOD file path:{APOD_path}')
        
        return save_image, apod_id
    
    # If the APOD image is already in the cache, return its ID
    if not image == 0:
        print('APOD image is already in cache')
        return image
    
    # Return 0 if the APOD image could not be added to the cache
    else:
        return 0
    
def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # Connect to the image cache DB
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    #defines the SQL statement to insert the APOD image information into the database.
    add_apod_query = """
        INSERT INTO image_apod
        (
         title, 
         explanation, 
         file_path, 
         sha256
        )
        VALUES (?, ?, ?, ?);
    """
    #creates a tuple containing
    #the APOD image information that will be inserted into the database.
    img = (title, explanation, file_path, sha256)
    
    # checks if the APOD image is already in the database by calling the get_apod_id_from_db function, 
    id = get_apod_id_from_db(sha256)
    if not id == 0 :
        return id
    
    # executes the SQL statement to insert the APOD image information into the database 
    cur.execute(add_apod_query,img)
    
    con.commit() 
    con.close()
    
    
def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # Connect to the image cache DB
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    # Query for the APOD record with the specified  hash value
    img_query = f""" 
     SELECT id FROM image_apod 
     WHERE sha256 = ? 
    """
    # Execute the query and fetch the results
    cur.execute(img_query, (image_sha256,))
    img_query_resltus =  cur.fetchone()
    
    # Check if the query returned no results
    if  img_query_resltus == None :
        return 0
    
    # otherwise it will return the ID of the APOD record
    if not  img_query_resltus == None: 
      return img_query_resltus[0]
    
    # Commit the changes to the database and close the connection
    con.commit()
    con.close()
    
def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # Remove leading and trailing spaces, replace inner spaces with underscores from the image title
    image_title = image_title.strip().replace(' ', '_')
    image_title = re.sub('[^A-Za-z0-9_]+', '', image_title)
    
    # Get the file extension from the image URL
    file_extension = image_url.split('.')[-1]
    
    # Combine the formatted image title and file extension to create the file name
    formatted_title = f"{image_title}.{file_extension}"
    
    # Join the image cache directory path with the formatted file name to create the full path
    full_path = os.path.join(image_cache_dir, formatted_title)
    
    return full_path
def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    # Construct a SELECT query to retrieve the APOD information for the given image ID
    select_apod_query = """ 
      SELECT title, explanation, file_path FROM image_apod 
      WHERE id = ?
    """
    
  # Execute the query with the given image ID as the parameter and retrieve the result
    cur.execute(select_apod_query, (image_id,))
    # retrieves a single row from the result set of a query that has been executed
    query_result = cur.fetchone()
    
    # Commit the changes to the database and close the connection
    con.commit()
    con.close()
    #  a dictionary to store the APOD information
    apod_info = {
            'title': query_result[0],
            'explanation': query_result[1],
            'file_path': query_result[2]
         }
  # If the query returned a result, return the APOD information dictionary
    if query_result != 0:
        return apod_info
    # Otherwise, return none
    else:
        return None
    


if __name__ == '__main__':
    main()
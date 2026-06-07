import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import sobel
from rasterio import MemoryFile
from io import BytesIO 

# Database connection details 
host = "localhost" 
port = "5432" 
dbname = "gme221_exer5" 
user = "postgres" 
password = "#Akonaito1234" 

def fetch_raster_from_db(): 
    """ 
    Fetch raster bytes and its bounding box from the PostgreSQL database. 
    
    Returns: 
        bytes: Raster data in byte format. 
        float: Minimum x-coordinate of the bounding box (EPSG:4326). 
        float: Minimum y-coordinate of the bounding box (EPSG:4326). 
        float: Maximum x-coordinate of the bounding box (EPSG:4326). 
        float: Maximum y-coordinate of the bounding box (EPSG:4326). 
    """ 
    print("Starting database connection...")

    # Establish the connection to the PostgreSQL database 
    try: 
        connection = psycopg2.connect( 
            host=host, 
            port=port, 
            dbname=dbname, 
            user=user,
            password=password 
        ) 
        print("Database connection established successfully.") 
    except Exception as e: 
        print(f"Error connecting to the database: {e}") 
        return None 
     
    cursor = connection.cursor() 
    print("Cursor created successfully.") 
     
    # SQL query to fetch raster data and its bounding box transformed to EPSG:4326 
    sql_query = """ 
        SELECT  
            ST_AsGDALRaster(rast, 'GTiff') AS raster_data,  
            ST_XMin(ST_Transform(ST_SetSRID(ST_Envelope(rast), 32651), 4326)) AS xmin, 
            ST_YMin(ST_Transform(ST_SetSRID(ST_Envelope(rast), 32651), 4326)) AS ymin, 
            ST_XMax(ST_Transform(ST_SetSRID(ST_Envelope(rast), 32651), 4326)) AS xmax, 
            ST_YMax(ST_Transform(ST_SetSRID(ST_Envelope(rast), 32651), 4326)) AS ymax 
        FROM public.dtm_table  
        WHERE rid = 1; 
    """ 
    print("Executing SQL query to fetch raster data and bounding box...") 
 
    try: 
        cursor.execute(sql_query) 
        print("SQL query executed successfully.") 
    except Exception as e: 
        print(f"Error executing the SQL query: {e}") 
        cursor.close() 
        connection.close() 
        return None 
 
    result = cursor.fetchone() 
 
    if result: 
        raster_data, xmin, ymin, xmax, ymax = result 
        print(f"Raster data and bounding box retrieved successfully.") 
        print(f"Bounding box coordinates (EPSG:4326): xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}") 
    else: 
        print("No data found for the given query.") 
        cursor.close() 
        connection.close() 
        return None 
 
    cursor.close() 
    connection.close() 
    print("Database connection closed.") 
 
    return raster_data, xmin, ymin, xmax, ymax


def generate_flood_hazard_map(raster_bytes, flood_threshold):
    """
    This funtion takes raster bytes and a flood threshold elevation as input,
    processes the raster to generate a flood hazard map, and returns the map as an image.
    
    Args:
        raster_bytes (bytes): The byte data representing the raster.
        flood_threshold (float): The elevation threshold for flood-prone areas.
        
    Returns:
        BytesIO: The PNG image of the flood hazard map.
    """
    # Read the raster data from the byte stream
    with MemoryFile(raster_bytes) as memfile:
        with memfile.open() as dataset:
            # Read the first band (elevation data)
            raster_array = dataset.read(1)

            # Compute flood hazard map (based on elevation)
            min_elevation = np.min(raster_array)
            print(f"Min elevation: {min_elevation} meters")

             # Create flood hazard mask (1 for flood-prone, 0 for safe) 
            flood_mask = raster_array <= flood_threshold + min_elevation 
            flood_hazard_map = flood_mask.astype(np.uint8) 
 
            # Calculate slope (optional refinement step) 
            sobel_x = sobel(raster_array, axis=0) 
            sobel_y = sobel(raster_array, axis=1) 
            slope = np.sqrt(sobel_x**2 + sobel_y**2) 
 
            # Refine flood hazard map based on slope threshold (optional) 
            slope_threshold = 1  # Example slope threshold 
            slope_mask = slope <= slope_threshold 
            refined_flood_hazard_map = flood_hazard_map & slope_mask 
 
            # Create a new image with an alpha channel (RGBA) where transparency is 0 
            height, width = refined_flood_hazard_map.shape 
            rgba_map = np.zeros((height, width, 4), dtype=np.uint8)  # Create a blank RGBA image 
 
            # Flooded areas (set to opaque blue, for example) 
            rgba_map[refined_flood_hazard_map == 1] = [0, 0, 255, 255]  # Blue color for flooded areas 
 
            # Non-flooded areas (set to fully transparent) 
            rgba_map[refined_flood_hazard_map == 0] = [0, 0, 0, 0]  # Transparent for non-flooded areas 
 
            # Visualize the flood hazard map using matplotlib with transparency 
            fig, ax = plt.subplots(figsize=(10, 8)) 
            ax.imshow(rgba_map) 
            ax.axis('off')  # Hide axis for cleaner visualization 
 
            # Save the image to a BytesIO object to send over Flask API 
            img_io = BytesIO() 
            plt.savefig(img_io, format='PNG', bbox_inches='tight', pad_inches=0, transparent=True) 
            img_io.seek(0) 
 
            # Return the image 
            return img_io 
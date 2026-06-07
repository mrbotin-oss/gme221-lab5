import os
from models import fetch_raster_from_db, generate_flood_hazard_map 
 
def main(): 
    """ 
    Main function to run the script and fetch the raster data. 
    """ 
    print("Starting the script...") 
 
    # Fetch raster data and bounding box from the database 
    raster_data, xmin, ymin, xmax, ymax = fetch_raster_from_db() 
 
    # Print the fetched data to verify 
    if raster_data: 
        print("Raster data fetched successfully.") 
        print(f"Raster data size: {len(raster_data)} bytes") 


        # Define flood threshold (elevation value, for example 10 meters) 
        flood_threshold = 10.0 
 
        # Generate the flood hazard map 
        print("Generating flood hazard map...") 
        flood_hazard_map = generate_flood_hazard_map(raster_data, flood_threshold) 
 
        # Define the path to save the image 
        save_path = "static/flood_hazard_map.png" 
         
        # Ensure the static folder exists 
        os.makedirs(os.path.dirname(save_path), exist_ok=True) 
 
        # Save the flood hazard map image to the specified path 
        with open(save_path, "wb") as f: 
            f.write(flood_hazard_map.getvalue()) 
 
        print(f"Flood hazard map generated and saved at: {save_path}") 
    else:
        print("Failed to fetch raster data.")
 
if __name__ == "__main__": 
    main() 
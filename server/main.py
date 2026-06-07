from models import fetch_raster_from_db 
 
def main(): 
    """ 
    Main function to run the script and fetch the raster data. 
    """ 
    print("Starting the script...") 
 
    # 1. Fetch into a single object first to prevent unpacking crashes
    result = fetch_raster_from_db() 
 
    # 2. Check if the database successfully handed over the data
    if result is not None: 
        # 3. Safe to unpack now!
        raster_data, xmin, ymin, xmax, ymax = result
        print("Raster data fetched successfully.") 
        print(f"Raster data size: {len(raster_data)} bytes") 
        print(f"Bounding box: Min({xmin}, {ymin}), Max({xmax}, {ymax})")
    else: 
        print("\n[-] Error: Failed to fetch raster data.") 
        print("    Your database table exists, but the query inside server/models.py returned nothing.") 
        print("    Please check the table name or columns specified in models.py.")
 
if __name__ == "__main__": 
    main()
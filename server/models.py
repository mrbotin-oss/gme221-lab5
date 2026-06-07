import psycopg2 

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
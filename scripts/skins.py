import json
import mysql.connector

# Function to read JSON file and return data
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to insert skins data into MySQL
def insert_skins_data(data):
    query = """
    INSERT INTO skins (skin_id, skin_name, rarity, max_wear, min_wear, skin_type, skin_desc, image_file, collection_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE skin_name=VALUES(skin_name), rarity=VALUES(rarity), max_wear=VALUES(max_wear), min_wear=VALUES(min_wear), skin_type=VALUES(skin_type), skin_desc=VALUES(skin_desc), image_file=VALUES(image_file), collection_id=VALUES(collection_id);
    """
    for item in data:
        # Directly use the rarity string from the JSON data
        rarity_string = item['rarity']['id']

        collection_id = ""    
        if 'collections' in item and item['collections']: 
            if item['collections']:
                collection_id = item['collections'][0]['id']
        
        cursor.execute(query, (item['id'], item['name'], rarity_string, item['max_float'], item['min_float'], item['weapon']['id'], item['description'], item['image'], collection_id))


# Function to insert skin images data into MySQL
def insert_skin_images_data(data):
    query = """
    INSERT INTO skin_images (skin_id_ungrouped, image_file) 
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE image_file=VALUES(image_file);
    """
    for item in data:
        cursor.execute(query, (item['id'], item['image']))

# Main execution block
if __name__ == "__main__":
    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'user': 'csuser',
        'port': 3306,
        'password': 'cs_sucks',
        'database': 'cstroll'
    }

    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Read JSON files
    skins_data = read_json('./data/skins.json')
    skin_images_data = read_json('./data/skins_not_grouped.json')

    # Insert data into MySQL tables
    insert_skins_data(skins_data)
    insert_skin_images_data(skin_images_data)

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully.")

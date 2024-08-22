import json
import mysql.connector

# Function to read JSON file and return data
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to insert collections data into MySQL
def insert_collections_data(data):
    query = """
    INSERT INTO collections (collection_id, collection_name, image_file) VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE collection_name=VALUES(collection_name), image_file=VALUES(image_file);
    """
    for item in data:
        cursor.execute(query, (item['id'], item['name'], item['image']))

# Function to insert cases data into MySQL
def insert_cases_data(data):
    query = """
    INSERT INTO cases (case_id, case_name, type, skin_list, image_file) 
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE case_name=VALUES(case_name), type=VALUES(type), skin_list=VALUES(skin_list), image_file=VALUES(image_file);
    """
    for item in data:
        # Extracting skin IDs from contains array
        skin_ids = ','.join([str(skin['id']) for skin in item.get('contains', [])])
        
        # Execute the query with the extracted data
        cursor.execute(query, (item['id'], item['name'], item['type'], skin_ids, item['image']))


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
    collections_data = read_json('./data/collections.json')
    cases_data = read_json('./data/cases.json')

    # Insert data into MySQL tables
    insert_collections_data(collections_data)
    insert_cases_data(cases_data)

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully.")

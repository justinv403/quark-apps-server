# Flask script to read data from the MySQL database and return it as a JSON object

# Dependencies
from flask import Flask, jsonify

# Import local dependencies
from db_connector import *

# Create a Flask app
app = Flask(__name__)

# Create the route to read the data from the database
@app.route('/api/db_reader', methods=['GET'])
def get_apps():
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        print("DB_READER: Unable to connect to the database")
        return None

    # Query the database
    with connection.cursor() as cursor:
        # Read all the apps from the database
        cursor.execute("SELECT * FROM apps")
        apps = cursor.fetchall()

    #
    print("DB_READER: Reading data from the database...")

    # Convert to a list of dictionaries
    apps_list = []
    for app in apps:
        apps_list.append({
            'app_id': app[0],
            'app_name': app[1],
            'app_version': app[2],
            'sha256_hash': app[3],
            'md5_hash': app[4],
            'last_updated': app[5],
            'filesize': app[6],
            'filename': app[7],
            'path': app[8]
        })

    # Close the connection
    connection.close()

    # Return the data as a JSON object
    return jsonify(apps_list)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
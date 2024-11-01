# Flask script to read data from the MySQL database and return it as a JSON object

# Dependencies
from flask import Flask, jsonify
import os
import pymysql

# Configure the DB connection
db_config = {
    'user': os.getenv('QUARK_DB_USER'),
    'password': os.getenv('QUARK_DB_PASS'),
    'host': os.getenv('QUARK_DB_HOST'),
    'database': os.getenv('QUARK_DB_NAME')
}

# Create a Flask app
app = Flask(__name__)

# Create the route to read the data from the database
@app.route('/api/db_reader', methods=['GET'])
def get_apps():
    # try:
    #     # Connect to the database
    #     connection = pymysql.connect(**db_config)

    #     # Query the database
    #     with connection:
    #         with connection.cursor() as cursor:
    #             # Read all the apps from the database
    #             cursor.execute("SELECT * FROM apps")
    #             apps = cursor.fetchall()

    #     # Convert to a list of dictionaries
    #     apps_list = []
    #     for app in apps:
    #         apps_list.append({
    #             'app_id': app[0],
    #             'app_name': app[1],
    #             'app_version': app[2],
    #             'md5_hash': app[3]
    #         })

    # except pymysql.Error as err:
    #     return jsonify({"error": str(err)}), 500
    
    # finally:
    #     # Close the connection
    #     connection.close()

    # Testing correct environment variables
    print(db_config)

    # For testing, provide a sample list of apps
    apps_list = [
        {
            'app_id': 1,
            'app_name': 'App 1',
            'app_version': '1.0.0',
            'md5_hash': '1234567890'
        },
        {
            'app_id': 2,
            'app_name': 'App 2',
            'app_version': '1.0.0',
            'md5_hash': '0987654321'
        },
        {
            'app_id': 3,
            'app_name': 'App 3',
            'app_version': '1.0.0',
            'md5_hash': '6789012345'
        },
        {
            'app_id': 4,
            'app_name': 'App 4',
            'app_version': '1.0.0',
            'md5_hash': '5432109876'
        }
    ]

    # Return the data as a JSON object
    return jsonify(apps_list)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
# Script to manage existing files in the database

# Dependencies
from flask import Flask, redirect, request
import os

# Import local dependencies
from db_connector import *
from db_scanner import *

# Create a Flask app
app = Flask(__name__)

# Set the global BASE_DIR variable
BASE_DIR = '/usr/share/nginx/html/apps'

# Create a route to upload a new file to the database
@app.route('/admin/upload', methods=['POST'])
def upload_file():
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Check if the file is in the request
    if 'app' not in request.files:
        return redirect(f'/error.html?error=No+file+part+in+the+request')

    # Create the cursor
    with connection.cursor() as cursor:
        # Get the file from the request
        file = request.files['app']
        if file.filename == '':
            return redirect(f'/error.html?error=No+selected+file')
        
        # Check if the file already exists in the database
        cursor.execute("SELECT * FROM apps WHERE filename = %s", (file.filename,))
        result = cursor.fetchone()
        if result:
            return redirect(f'/error.html?error=File+already+exists+in+the+database')

        # Save the file to the filesystem
        file_path = os.path.join(BASE_DIR, file.filename)
        file.save(file_path)

        # Get the app version from the form
        app_version = request.form['app_version']

        # Calculate the SHA256 hash of the file
        sha256_hash = calculate_sha256(file_path)

        # Calculate the MD5 hash of the file
        md5_hash = calculate_md5(file_path)

        # Insert the file into the database
        cursor.execute("INSERT INTO apps (app_name, app_version, sha256_hash, md5_hash, filesize, filename, path) VALUES (%s, %s, %s, %s, %s, %s, %s)", (file.filename, app_version, sha256_hash, md5_hash, os.path.getsize(file_path), file.filename, file_path))
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')


# Create a route to scan for new files in the database
@app.route('/admin/scan', methods=['GET'])
def scan():
    # Call the function from the db_scanner.py file
    scan_apps()

    # Return the user to the admin page
    return redirect('/')


# Create a route to remove a file from the database
@app.route('/admin/delete/<int:app_id>', methods=['GET'])
def delete_file(app_id):
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
        return None

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the file
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

        # Try to delete the file from the filesystem using the file_path from the database
        try:
            os.remove(result[8])
        except:
            return redirect(f'/error.html?error=Unable+to+delete+file+from+the+filesystem')

        # Check if the file exists in the database
        if not result:
            return redirect(f'/error.html?error=Unable+to+delete+file+from+the+filesystem')

        # Delete the file from the database
        cursor.execute("DELETE FROM apps WHERE app_id = %s", (app_id,))
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')


# Function to recompute the database
@app.route('/admin/recompute', methods=['GET'])
def db_recompute():
    # Print running message
    print("DB_RECOMPUTE: Beginning database recompute...")

    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        print("DB_RECOMPUTE: Unable to connect to the database")
        return
    
    # Attempt app_id recompute
    try:
        # Recompute the app_id column
        with connection.cursor() as cursor:
            # Drop the column
            cursor.execute("ALTER TABLE apps DROP COLUMN app_id")
            # Add the column back
            cursor.execute("ALTER TABLE apps ADD COLUMN app_id INT PRIMARY KEY AUTO_INCREMENT FIRST")
            connection.commit()
    except:
        # If the recompute fails, print an error message
        print("DB_RECOMPUTE: Error recomputing app_id column")
        return redirect(f'/error.html?error=Error+recomputing+app_id+column')
    
    finally:
        # Close the connection
        print("DB_RECOMPUTE: Recompute successful")
        connection.close()

        # Return the user to the admin page
        return redirect('/')


# Function to redirect the user to the correct update page for an app
@app.route('/admin/update/<int:app_id>', methods=['GET'])
def update_file(app_id):
    return redirect(f'/update.html?app_id={app_id}')

# Function to update the file in the database
@app.route('/admin/update', methods=['POST'])
def update_file_post():
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')

    # Check if the file is in the request
    if 'app' not in request.files:
        return redirect(f'/error.html?error=No+file+part+in+the+request')

    # Create the cursor
    with connection.cursor() as cursor:
        # Get the file from the request
        file = request.files['app']
        if file.filename == '':
            return redirect(f'/error.html?error=No+selected+file')

        # Get the app_id from the form
        app_id = request.form['app_id']

        # Query the database for the existing file information
        cursor.execute("SELECT filename FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

        if not result:
            return redirect(f'/error.html?error=App+ID+not+found+in+the+database')

        # Use the filename from the database
        file_path = os.path.join(BASE_DIR, result[0])
        
        # Save the updated file to the filesystem
        file.save(file_path)

        # Get the app version from the form
        app_version = request.form['app_version']

        # Calculate the SHA256 hash of the file
        sha256_hash = calculate_sha256(file_path)

        # Calculate the MD5 hash of the file
        md5_hash = calculate_md5(file_path)

        # Update the file in the database
        cursor.execute("UPDATE apps SET app_version = %s, sha256_hash = %s, md5_hash = %s, filesize = %s, filename = %s, path = %s WHERE app_id = %s", (app_version, sha256_hash, md5_hash, os.path.getsize(file_path), result[0], file_path, app_id))

        # Commit the changes
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
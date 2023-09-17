from accesslink import AccessLink
from google.cloud import storage
from cloudevents.http import CloudEvent
import functions_framework
import xmltodict
from datetime import datetime
import json
from time import sleep
import google.cloud.logging
import logging
import os

# Initialize environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
BUCKET = os.environ.get('BUCKET')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
USER_ID = os.environ.get('USER_ID')

# Define global constants
RETRIES = 3
DELAY_CS = 5
DELAY_BQ = 10

# Initialize Google Cloud Logging client and set up logging for the application
client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

@functions_framework.cloud_event
def polar_to_gcs(cloud_event: CloudEvent) -> None:
    """Main function to process the Polar data and upload it to GCS."""

    # Initialize the GCS client
    storage_client = storage.Client() 

    # Create a transaction using provided credentials
    accesslink = AccessLink(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    logging.info("Creating transaction.")
    transaction = accesslink.training_data.create_transaction(user_id=USER_ID, access_token=ACCESS_TOKEN)

    if transaction is None:
        logging.error("No new data available. Transaction could not be created.")
        return

    # Extract the list of exercises from the transaction
    logging.info("Fetching list of exercise URLs.")
    resource_urls = transaction.list_exercises()["exercises"]

    if resource_urls:
        logging.info(f"Start uploading {len(resource_urls)} exercise(s).")
        for idx, url in enumerate(resource_urls):
            try:
                # Fetch exercise data from the transaction
                exercise_dict = transaction.get_exercise_summary(url)
                
                # Get GPX data
                gpx_data = transaction.get_gpx(url)

                # If gpx_data is not empty, parse and merge with exercise_dict
                if gpx_data:
                    gpx_dict = xmltodict.parse(gpx_data, dict_constructor=dict, attr_prefix='', cdata_key='text')
                    exercise_dict = exercise_dict | gpx_dict

                # Prepare for upload
                bucket = storage_client.bucket(BUCKET)
                exercise_id = exercise_dict['id']
                date_str = exercise_dict['start-time']
                date_format = '%Y-%m-%dT%H:%M:%S'
                date_obj = datetime.strptime(date_str, date_format)
                formatted_date = date_obj.strftime('%Y-%m-%d')
                dataset_file = f'polar_{exercise_id}_{formatted_date}'
                path = f'polar/{dataset_file}.json'
                
                # Retry mechanism for uploading to GCS
                for attempt in range(RETRIES):
                    try:
                        blob = bucket.blob(path)
                        blob.upload_from_string(json.dumps(exercise_dict), content_type="application/json")
                        logging.info(f"Exercise {exercise_id} uploaded to gs://{BUCKET}/{path}")
                        break
                    except Exception as e:
                        if attempt == RETRIES - 1:
                            raise
                        logging.error(f"Error uploading {exercise_id} on attempt {attempt + 1}: {e}")
                        sleep(DELAY_CS)

                # Introduce a delay between uploads to avoid exceeding BigQuery's metadata update rate limits.
                # However, we skip the delay after the last upload to prevent unnecessary waiting.
                if idx < len(resource_urls) - 1:
                    sleep(DELAY_BQ)
            except Exception as e:
                logging.error(f"Error during processing of URL {url}: {e}")
                return

    # Commit the transaction 
    logging.info("Committing transaction.")
    transaction.commit()

from google.cloud import bigquery
import functions_framework
import google.cloud.logging
import logging
from cloudevents.http import CloudEvent
import os

PROJECT_ID = os.environ.get('PROJECT_ID')
ZONE = os.environ.get('ZONE')
DATASET = os.environ.get('DATASET')

# Initialize Google Cloud Logging client and set up logging for the application
client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

@functions_framework.cloud_event
def gcs_to_gbq(cloud_event: CloudEvent) -> None:
    """
    Load data from Google Cloud Storage to Google BigQuery.

    This function is triggered by a Cloud Event when new data is available in
    a specific GCS bucket. It then processes and loads this data to a specific
    BigQuery table.
    """

    # Parse cloud event data.
    data = cloud_event.data
    bucket = data['bucket']
    name = data['name']
    source = name.split('/')[0]

    logging.info(f"Starting to load data from {name} in {bucket} to BigQuery.")

    # Construct a BigQuery client object.
    client = bigquery.Client()

    # Set table_id based on source.
    table_id = f'{PROJECT_ID}.{DATASET}.{source}_training'

    # Get the number of rows in the table before the load operation.
    destination_table = client.get_table(table_id)
    rows_before_load = destination_table.num_rows
    
    # Define configuration for the BigQuery load job.
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    uri = f'gs://{bucket}/{name}'

    # Attempt to load data from GCS to BigQuery.
    try:  
        load_job = client.load_table_from_uri(
            uri,
            table_id,
            location=ZONE,  
            job_config=job_config,
        )  # Make an API request.

        load_job.result()  # Waits for the job to complete.

        # Get the number of rows in the table after the load operation.
        destination_table = client.get_table(table_id)
        rows_after_load = destination_table.num_rows
        rows_added = rows_after_load - rows_before_load
    except Exception as e:
        logging.error(f"Error while loading data from {uri} to BigQuery: {e}")
        return

    logging.info(f'Loaded {rows_added} row(s) from {uri}.')


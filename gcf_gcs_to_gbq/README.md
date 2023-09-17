# gcs_to_gbq: Google Cloud Storage to Google BigQuery Data Loader

The `gcs_to_gbq` function is an event-driven service that listens for Cloud Events corresponding to new data uploads to Google Cloud Storage (GCS). Once triggered, it processes and loads the data from GCS into a Google BigQuery table.

## Environment Variables

The function uses the following environment variables. The variables will be set with function deployment.

- **PROJECT_ID**: Your Google Cloud project ID.
- **ZONE**: The location of the BigQuery dataset, e.g., `europe-west3`.
- **DATASET**: The name of the BigQuery dataset where the data should be loaded.

## Dependencies

- `google.cloud`: Google Cloud Python Client Library, particularly BigQuery.
- `cloudevents`: Library to handle CloudEvents in Python.
- `functions_framework`: Framework for writing lightweight Python Cloud Functions.

## Functions

- `gcs_to_gbq(cloud_event: CloudEvent) -> None`:
  - The main function that processes the CloudEvent, loads data from the specified GCS bucket, and writes it to a BigQuery table.

## Flow

1. Parse CloudEvent data to identify the GCS bucket and the uploaded file.
2. Construct a BigQuery client object and set the appropriate table based on the source of the data.
3. Configure the BigQuery load job with relevant parameters.
4. Load the data from GCS into BigQuery.

## Error Handling

The function comes with built-in error handling to capture any issues during the loading process from GCS to BigQuery and logs them for debugging.

## Logging

The function employs Google Cloud Logging for monitoring, making it convenient to debug and monitor operations through the Google Cloud Console.

## Deployment

To deploy this function to Google Cloud Functions, use the `gcloud` CLI:

```bash
gcloud functions deploy python-finalize-function \
--gen2 \
--runtime=python311 \
--region=YOUR_REGION \
--source=. \
--entry-point=gcs_to_gbq \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=YOUR_BUCKET" \
--set-env-vars PROJECT_ID=YOUR_PROJECT_ID,ZONE=YOUR_ZONE,DATASET=YOUR_DATASET
```

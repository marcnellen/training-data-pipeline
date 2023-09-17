# polar_to_gcs: Polar Data Processor for Google Cloud Storage

The `polar_to_gcs` function is designed to process incoming data from Polar and upload it to Google Cloud Storage (GCS). It integrates with the AccessLink API to fetch exercise summaries and associated GPX data, and then uses Google Cloud Storage's Python Client Library to store the data.

## Environment Variables and Secrets

The function uses the following environment variables. The variables will be set with function deployment.

- **PROJECT_ID**: Your Google Cloud project ID.
- **BUCKET**: Name of the GCS bucket where the data should be uploaded.

Create the folloing secrets with Secret Manager. The secrets will be deployed as environment variables with function deployment.

- **CLIENT_ID**: AccessLink client ID.
- **CLIENT_SECRET**: AccessLink client secret.
- **ACCESS_TOKEN**: AccessLink access token for the user.
- **USER_ID**: ID of the user in the AccessLink platform.

## Dependencies

- `accesslink`: Library to integrate with the AccessLink API.
- `google.cloud`: Google Cloud Python Client Library.
- `cloudevents`: Library to handle CloudEvents in Python.
- `functions_framework`: Framework for writing lightweight Python Cloud Functions.
- `xmltodict`: Library to parse XML into Python dictionaries.
- `datetime`: Module for manipulating dates and times.

## Functions

- `polar_to_gcs(cloud_event: CloudEvent) -> None`:
  - The main function that processes the CloudEvent triggered by Polar, fetches the data from AccessLink, and uploads it to the specified GCS bucket.

## Flow

1. Initialize the GCS client and create a transaction using the provided AccessLink credentials.
2. Fetch the list of exercise URLs from the transaction.
3. For each URL:
   - Fetch the exercise summary and GPX data.
   - Merge the two data sources, convert to JSON format, and upload to GCS.
4. Commit the transaction after processing all URLs.

## Error Handling and Retries

The function has built-in error handling mechanisms. If an upload to GCS fails, the function will retry up to a specified number of times (`RETRIES`). There is also a delay introduced between consecutive uploads (`DELAY_BQ`) to avoid BigQuery rate limits.

## Logging

The function uses Google Cloud Logging for logging, enabling monitoring and debugging through the Google Cloud Console.

## Deployment

To deploy this function to Google Cloud Functions, you can use the `gcloud` CLI:

```bash
gcloud functions deploy python-pubsub-function \
--gen2 \
--runtime=python311 \
--region=YOUR_REGION \
--source=. \
--entry-point=polar_to_gcs \
--trigger-topic=YOUR_TOPIC \
--set-env-vars PROJECT_ID=YOUR_PROJECT_ID,BUCKET=YOUR_BUCKET \
--set-secrets "CLIENT_ID=CLIENT_ID:latest","CLIENT_SECRET=CLIENT_SECRET:latest","ACCESS_TOKEN=ACCESS_TOKEN:latest","USER_ID=USER_ID:latest"
```

# Polar Data Integration Pipeline

This project implements a data integration pipeline that receives data from [Polar Accesslink API v3](https://www.polar.com/accesslink-api/#polar-accesslink-api), stores it in Google Cloud Storage (GCS), and then loads it into Google BigQuery for further individual analytics.

Although Polar Accesslink API provides endpoints for extensive data extraction possibilities, such as user data, daily activity, sleep, etc., the project is narrowed down to an area primarily relevant to running sports. The endpoints currently implemented are used for the extraction of exercise summary data and GPX data for a specific user.

## Project Overview

The pipeline consists of three main functions:

1. **Webhook Handler (acl_webhook)**:
   - Receives webhooks from Polar as notification, that new training data is available.
   - Validates the integrity of the webhook.
   - Publishes relevant data to a Pub/Sub topic.

2. **GCS Data Uploader (polar_to_gcs)**:
   - Listens to a Pub/Sub topic.
   - Retrieves new available training data from Polar via AccessLink.
   - Stores the data in JSON format in a GCS bucket.

3. **BigQuery Data Loader (gcs_to_gbq)**:
   - Triggered by Cloud Events when new data is available in GCS.
   - Loads the data from GCS into a BigQuery table.

## Prerequisites

- Execute the [How to get started](https://www.polar.com/accesslink-api/#how-to-get-started) from Polar Accesslink API to obtain:
    - client id
    - client secret
    - access token
    - user id
- Set-up a Google Cloud Project.
- Enable Google Cloud APIs and Service Accounts: Cloud Functions, Pub/Sub, Cloud Storage, BigQuery.
- Create a Pub/Sub topic that is used as trigger for the GCS Data Uploader.
- Configure environment variables and secrets for each function, as described in the respective READMEs.
- Configure a BigQuery dataset and table with the following [schema](./gcf_gcs_to_gbq/schema.json)

> :information_source: **Note:** The application currently doesn't handle authorization flows! In case the access token has expired, you must manually request a new one through the token endpoint."

## Installation & Deployment

1. **Setup**:
   - Set up the Google Cloud SDK and `gcloud` CLI on your machine.
   - Authenticate with your Google Cloud account: `gcloud auth login`.

2. **Deploying the Functions**:
   Each function can be deployed using the `gcloud functions deploy` command. Refer to the specific READMEs for each function for more details.

3. **Monitoring**:
   - Use the Google Cloud Console to monitor logs and check for errors.
   - Logging is integrated into each function, making it easy to track important events and potential issues.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

# acl_webhook: Webhook Processor for Polar Events

This is a Python-based webhook handler designed to process incoming webhook events from Polar. It verifies the data's integrity using HMAC and, upon successful verification, publishes the relevant data to a Google Pub/Sub topic.

## Environment Variables and Secrets

The function uses the following environment variables. The variables will be set with function deployment.

- **PROJECT_ID**: Your Google Cloud project ID.
- **TOPIC**: The Pub/Sub topic where you want to publish the incoming data.

Create the folloing secret with Secret Manager. The secret will be deployed as environment variable with function deployment.

- **SIGNATURE_SECRET_KEY**: The secret key used for verifying the incoming webhook's HMAC signature.

## Dependencies

- `functions_framework`: Framework for writing lightweight Python Cloud Functions.
- `google.cloud`: Google Cloud Python Client Library.
- `flask`: Micro web framework written in Python.
- `hmac` and `hashlib`: Libraries for handling cryptographic operations.

## Functions

- `_verify_webhook(data: str, secret_key: str, signature: str) -> bool`:
  - Verifies the integrity of the webhook data using HMAC. Compares the calculated HMAC using the provided secret key against the given signature.

- `_publish_to_pubsub(request: Request, project_id: str, topic: str) -> None`:
  - Publishes the request payload to the specified Pub/Sub topic.

- `acl_webhook(request: Request) -> Tuple[str, int]`:
  - The main function that handles incoming webhook requests. It checks the event type from the headers, verifies the webhook signature, and then publishes the data to a Pub/Sub topic if the verification is successful.

## Supported Events

Currently, the function handles two types of Polar webhook events:

- `PING`: A health check event type, that is used to register the webhook.
- `EXERCISE`: An event type that contains exercise-related data.

For unsupported event types, the function logs the event type and returns a `400 Bad Request` response.

## Logging

The function uses Google Cloud Logging for logging, so you can monitor and debug the function using Cloud Logging in the Google Cloud Console.

## Security

The function verifies the incoming webhook's HMAC signature using the secret key (specified in the environment variables) before processing it, ensuring the integrity and authenticity of the data. If the verification fails, the function does not process the event.

## Deployment

To deploy this function to Google Cloud Functions, you can use the `gcloud` CLI:

```bash
gcloud functions deploy python-http-function \
--gen2 \
--runtime=python311 \
--region=YOUR_REGION \
--source=. \
--entry-point=acl_webhook \
--trigger-http \
--allow-unauthenticated \
--set-env-vars PROJECT_ID=YOUR_PROJECT_ID,TOPIC=YOUR_TOPIC \
--set-secrets "SIGNATURE_SECRET_KEY=SIGNATURE_SECRET_KEY:latest"
```

After deployment register the webhook as described under [Create webhook](https://www.polar.com/accesslink-api/#create-webhook) and pass the assigned function url in the request body.

To obtain the url after function deployment, you can use the `gcloud` CLI:

```bash
gcloud functions describe python-http-function \
--gen2 \
--region=YOUR_REGION \
--format="value(serviceConfig.uri)"
```

Save the `signature_secret_key` from the response. You will need it to verify incoming webhooks. Refer to [Environment Variables and Secrets](#environment-variables-and-secrets) for further instructions.

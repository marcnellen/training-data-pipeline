import functions_framework
from google.cloud import pubsub_v1
from flask import Request, abort
from typing import Tuple
import json
import hmac
import hashlib
import google.cloud.logging
import logging
import os

# Initialize environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
TOPIC = os.environ.get('TOPIC')
SIGNATURE_SECRET_KEY = os.environ.get('SIGNATURE_SECRET_KEY')

# Initialize Google Cloud Logging client and set up logging for the application
client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()


def _verify_webhook(data: str, secret_key: str, signature: str) -> bool:
    """
    Verify the integrity of the webhook data using HMAC.

    This function calculates the HMAC of the given data using the provided secret key
    and compares it to the provided signature to ensure the data's integrity.
    """

    hashed = hmac.new(secret_key.encode('utf-8'), data.encode('utf-8'), digestmod=hashlib.sha256)
    return hmac.compare_digest(hashed.hexdigest(), signature)

def _publish_to_pubsub(request: Request, project_id: str, topic: str) -> None:
    """
    Publish the request payload to a specified Pub/Sub topic.
    """
    
    # Initialize Pub/Sub client
    publisher = pubsub_v1.PublisherClient()
    
    # Construct full topic name
    topic_name = f'projects/{project_id}/topics/{topic}'

    # Extract JSON payload from request and publish to Pub/Sub
    payload = request.get_json()
    future = publisher.publish(topic_name, json.dumps(payload).encode('utf8'))
    
    # Wait for the publish operation to complete
    future.result()

@functions_framework.http
def acl_webhook(request: Request) -> Tuple[str, int]:
    """
    Handle webhook requests.

    This function processes incoming webhooks, verifies the webhook signature,
    and publishes relevant data to a Pub/Sub topic based on the webhook event.
    """

    # Retrieve request headers
    headers = request.headers
    
    # Ensure the request method is POST, otherwise abort
    if request.method != 'POST':
        abort(400)

    # Retrieve event type from the headers
    event_type = headers.get('polar-webhook-event')
    logging.info(f"Received event type: {event_type}")
    if not event_type:
        return 'Missing event type', 400

    # Handle PING event type
    if event_type == 'PING':
        return 'Success', 200

    # Handle EXERCISE event type
    elif event_type == 'EXERCISE':
        # Extract signature from the headers
        polar_webhook_signature = headers.get('polar-webhook-signature')
        if not polar_webhook_signature:
            return 'Missing signature', 400

        # Get the data payload from the request
        data = request.get_data(as_text=True)

        # Verify the signature of the webhook
        try:
            if _verify_webhook(data, SIGNATURE_SECRET_KEY, polar_webhook_signature):
                # If verification is successful, publish data to Pub/Sub
                try:
                    _publish_to_pubsub(request, PROJECT_ID, TOPIC)
                    logging.info("Event data successfully published to Pub/Sub.")
                    return 'Success', 200
                except Exception as e:
                    logging.error(f"Error publishing to Pub/Sub: {e}")
                    return "Failed to publish event", 500
            else:
                return 'Verification failed', 400
        except Exception as e:
            logging.error(f"Error during webhook verification: {e}")
            return "Internal server error", 500
    else:
        logging.info(f"Received unsupported event type: {event_type}")
        return 'Event not supported', 400

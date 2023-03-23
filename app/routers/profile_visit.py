from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from ..app_models.models import ProfileVisitedInput, ProfileVisitedEntry
from datetime import datetime
from google.cloud import pubsub_v1
import os
import json
from ..constants import PUB_SUB_TOPIC_PATH

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "profile-tracker-key.json"


# Set up the Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = PUB_SUB_TOPIC_PATH


router = APIRouter()


@router.post(
    "/visited-profile",
    tags=["Profile Visit"],
    description="""Processes information that visitor_id visited the profile of user_id.""",
)
async def visited_profile(profile_visited_input: ProfileVisitedInput):
    visited_entry = ProfileVisitedEntry(
        user_id=profile_visited_input.user_id,
        visitor_id=profile_visited_input.visitor_id,
        visited_at=datetime.now(),
    )

    visited_entry = jsonable_encoder(visited_entry)
    visited_entry = json.dumps(visited_entry).encode("utf-8")

    try:
        # Publish the message to the topic
        future = publisher.publish(topic_path, data=visited_entry)
        # Wait for the message to be published
        pub_sub_message_id = future.result()
        print(f"Message published with ID: {pub_sub_message_id}")

        return {
            "success": True,
            "pub_sub_message_id": pub_sub_message_id,
            "message": "Successfully added profile visited entry added successfully!",
        }

    except:

        return {
            "success": False,
            "message": "Could not add profile visited entry added successfully!",
        }

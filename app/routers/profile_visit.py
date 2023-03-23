from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from google.cloud import pubsub_v1, bigquery
import os
import json
from ..constants import PUB_SUB_TOPIC_PATH, PROJECT_ID, DATASET_ID
from ..app_models.models import ProfileVisitedInput, ProfileVisitedEntry

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


@router.get(
    "/visited-profile/{user_id}",
    tags=["Profile Visit"],
    description="""Provides details of visitors given user_id's profile in the last N days""",
)
async def get_visitors(user_id: str, N: int = 30):
    try:
        bq_client = bigquery.Client()
        query_job = bq_client.query(
            f"""
            SELECT DISTINCT visitor_id 
            FROM `{PROJECT_ID}.{DATASET_ID}.visit_records`
            WHERE user_id = '{user_id}'
            AND visited_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {N} DAY)
            ORDER BY visited_at DESC
        """
        )
        results = query_job.result()
        visitor_ids = [row[0] for row in results]
        visitor_count = len(visitor_ids)

        return {
            "user_id": user_id,
            "days": N,
            "visitor_count": visitor_count,
            "visitor_ids": visitor_ids,
            "message": f"{visitor_count} users visited the profile of user_id = '{user_id}' in the last {N} days",
        }

    except:
        return {
            "success": False,
            "message": "Could not fetch data from the BigQuery!",
        }

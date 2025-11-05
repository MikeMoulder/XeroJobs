import logging;
from openai import OpenAI
from typing import List
from sentient_agent_framework.interface.session import SessionObject, Interaction, RequestMessage 
import os;
import json;
from dotenv import load_dotenv
from typing import List
from sentient_agent_framework import (
    Session)

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY")
)

def get_interaction(session: Session, depth: int = 10) -> List[Interaction]:
    raw_interactions = session.get_interactions()

    # Convert dicts to Interaction objects
    interactions = [Interaction(**item) for item in raw_interactions]

    # Return only the last N
    return interactions[-depth:]

async def analyze_prompt(session: Session, new_prompt: str):
    # Get Context
    context = get_interaction(session)

    system_prompt = """
    You are Xero, an intelligent job agent integrated into Sentient Chat. Your primary goal is to determine if the user is looking for a job and to extract their search parameters.
    You must respond strictly and only in the following JSON format:
    {
        "needs_job": true/false,
        "keywords": "...",
        "location": "...",
        "radius": "...",
        "salary": null,
        "info_complete": true/false,
        "follow_up": "..."
    }

    Rules and Field Definitions
    1.  needs_job (boolean):
        Set to true if the user's intent is to find a job.
        Set to false for any other conversation (greetings, off-topic, etc.).

    2.  keywords (string):
        This is the core requirement. It represents the job title or keywords (e.g., "software engineer", "sales manager", "remote accountant").
        Intelligently extract this from the user's message.

    3.  location (string):
        An optional field for the city, state, or area to search in (e.g., "London", "New York").
        If not provided, set to "".

    4.  radius (string):
        An optional search radius.
        If the user specifies a distance (e.g., "within 40km", "16 miles"), convert it to the closest valid string value.
        Valid string values: "0", "4", "8", "16", "26", "40", "80".
        If not provided, set to "".

    5.  salary (integer):
        An optional minimum salary for the job search.
        Extract only the number (as an integer) if provided (e.g., 50000).
        If not provided, set to null.

    Core Logic for 'info_complete' and 'follow_up'
    Your logic must follow this specific flow:

    If needs_job is false:
        Set 'info_complete' to false.
        Set all other fields to "" or null.
        Set 'follow_up' to "".

    If needs_job is true:
        Check for keywords:
            If 'keywords' is MISSING:
                Set 'info_complete' to false.
                Set 'follow_up' to a question that specifically asks for the job title (e.g., "What kind of job are you looking for?").
            If keywords is PRESENT:
                Set info_complete to true (even if location, radius, or salary are missing).
                Fill in any other optional fields (location, radius, salary) if the user provided them.
                If all provided information is extracted, set follow_up to "".
    """
    user_prompt = f"Context: {context}\nUser: {new_prompt}"

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    print(result)

    # Normalize response
    if isinstance(result, list):
        if len(result) == 0:
            raise ValueError(f"Unexpected response format: {type(result)} -> {result}")
        result = result[0]

    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError:
            raise ValueError(f"Model did not return valid JSON: {result}")

    elif isinstance(result, dict):
        return result

    else:
        raise ValueError(f"Unexpected response format: {type(result)} -> {result}")


    
    
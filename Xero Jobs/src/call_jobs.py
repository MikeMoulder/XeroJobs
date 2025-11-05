from openai import AsyncOpenAI
from analyzer import *
import os
import json, ast
import http.client
from sentient_agent_framework import (
    Session)

client = AsyncOpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY")
)

# --- Your API Code ---
host = 'jooble.org'
key = os.getenv("JOBBLE_API_KEY")

def parse_json(jsonResponse):
    try:
        return json.loads(jsonResponse)
    except json.JSONDecodeError:
        return ast.literal_eval(jsonResponse)  # safely parse Python literal

def get_jobs(jsonResponse):

    data = parse_json(jsonResponse)

    # Parameters
    api_params = {
        "keywords": data["keywords"],
        "location": data["location"]
    }

#    Conditionally add optional fields *only if* they have a value.
#    This prevents sending '{"salary": null}' or '{"radius": ""}'
#    if the user didn't provide them.
    if data["radius"]:
        api_params["radius"] = data["radius"]
        
    if data["salary"] is not None:
        api_params["salary"] = data["salary"]

    if data["location"]:
        api_params["location"] = data["location"]

#    Convert the Python dictionary into a JSON string
#    This is the 'body' for your request.
    body = json.dumps(api_params)

    # --- Now, make the request ---
    print(f"Sending API request with body: {body}")

    connection = None
    try:
        connection = http.client.HTTPConnection(host)
        
        # Request headers
        headers = {"Content-type": "application/json"}
        
        # Send the request
        connection.request('POST', '/api/' + key, body, headers)
        
        # Get the response
        response = connection.getresponse()
        
        print(response.status, response.reason)
        
        # Read and print the response data
        response_data = response.read()
        clean_data = response_data.decode('utf-8') # Decode for clean printing
        print (clean_data) 

        return clean_data

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if connection is not None:
            connection.close()
    
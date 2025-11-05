from sentient_agent_framework import (
    AbstractAgent,
    DefaultServer,
    Session,
    Query,
    ResponseHandler)
from analyzer import *
from general import *
from call_jobs import *
from stream_response import *


class JobAgent(AbstractAgent):
    def __init__(
            self,
            name: str = "Xero Jobs"
    ):
        super().__init__(name)

    async def assist(
            self,
            session: Session,
            query: Query,
            response_handler: ResponseHandler
    ):
        # Analyse prompt
        await response_handler.emit_text_block(
            "Analyze", "Xero is analyzing your prompt..."
        )

        # Responsible for holding the results of the analyzed query of the user.
        result = await analyze_prompt(session, query.prompt)
        final_result = result[0] if isinstance(result, list) and result else result

        #holds the unproceesed job data collected from API
        data_source = ''

        # Access needs_job and check if true or false
        # Support both dict-like results and objects with attributes to avoid indexing errors.
        needs_job = None
        follow_up = None
        if isinstance(final_result, dict):
            needs_job = final_result.get("needs_job")
            follow_up = final_result.get("follow_up")
        else:
            needs_job = getattr(final_result, "needs_job", None)
            follow_up = getattr(final_result, "follow_up", None)

        if needs_job:
            print("User is looking for a job!")
            
            # Check if follow-up is needed
            if follow_up:
                print(f"Follow-up question: {follow_up}")
            else:
                #Get jobs from the API call and save them raw to the data_source.
                data_source = get_jobs(str(final_result))
        else:
            print("User is not looking for a job...routing to major LLM")
            
        if data_source:
                # Use response handler to emit JSON to the client
                await response_handler.emit_json(
                    "SOURCES", {"results": data_source}
                )
        
        if data_source:
            # Process job results
            # Use response handler to create a text stream to stream the final response to the client
            final_response_stream = response_handler.create_text_stream(
                "FINAL_RESPONSE"
                )
            async for chunk in stream_job_response(data_source):
                # Use the text stream to emit chunks of the final response to the client
                await final_response_stream.emit_chunk(chunk)
            # Mark the text stream as complete
            await final_response_stream.complete()
            # Mark the response as complete
            await response_handler.complete()
        else:
            # Process general query
            final_response_stream = response_handler.create_text_stream(
                "FINAL_RESPONSE"
                )
            async for chunk in generalQuery(session, query.prompt):
                # Use the text stream to emit chunks of the final response to the client
                await final_response_stream.emit_chunk(chunk)
            # Mark the text stream as complete
            await final_response_stream.complete()
            # Mark the response as complete
            await response_handler.complete()
        
if __name__ == "__main__":
    # Create an instance of a SearchAgent
    agent = JobAgent(name="Xero Jobs")
    # Create a server to handle requests to the agent
    server = DefaultServer(agent)
    # Run the server
    server.run()
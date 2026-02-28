"""
Chat Router
============
Defines the endpoint for the AI analyst chatbot powered by LangChain.

KEY CONCEPT: STREAMING RESPONSES
----------------------------------
LLMs generate text token by token. If you wait for the full response before
sending anything, users stare at a blank screen for 5–10 seconds.

Streaming sends each token as it's generated — the UI updates in real-time.
FastAPI supports this with StreamingResponse + async generators.

In the React frontend, you'll use the native Fetch API with ReadableStream
to consume the stream. (Axios doesn't handle streaming well — use fetch here.)

IMPLEMENTATION ORDER (recommended):
--------------------------------------
1. First, get a non-streaming version working:
   - Call agent.invoke({"input": message}) and return the full string
   - Confirm the chatbot works end to end

2. Then add streaming:
   - Switch to agent.astream_events() for token-by-token output
   - Wrap in StreamingResponse

LEARN MORE:
  FastAPI StreamingResponse: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
  LangChain streaming:       https://python.langchain.com/docs/concepts/streaming/
  Fetch ReadableStream:      https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.agents.churn_analyst import get_agent

router = APIRouter()


class ChatRequest(BaseModel):
    """
    Pydantic validates that incoming POST bodies match this shape.
    If `message` is missing or the wrong type, FastAPI auto-returns a 422 error.

    player_context: the full response from GET /api/v1/players/{platform}/{id}.
    Pass this when the user is viewing a player — gives the LLM real data to work with.

    conversation_history: previous messages so the LLM remembers context.
    Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    message: str
    player_context: dict | None = None
    conversation_history: list[dict] = []


@router.post("")
async def chat(request: ChatRequest):
    """
    Main chat endpoint — streams the LangChain agent's response token by token.

    The frontend sends:
      POST /api/v1/chat
      { "message": "Why is this player at risk?", "player_context": {...} }

    TODO: Implement this endpoint.

    STEP 1 — Non-streaming version (start here):
      agent = get_agent()
      result = agent.invoke({
          "input": request.message,
          "player_context": request.player_context,
          "chat_history": request.conversation_history,
      })
      return {"response": result["output"]}

    STEP 2 — Streaming version (add once step 1 works):
      async def generate():
          async for event in agent.astream_events({...}, version="v2"):
              if event["event"] == "on_chat_model_stream":
                  chunk = event["data"]["chunk"].content
                  if chunk:
                      yield chunk

      return StreamingResponse(generate(), media_type="text/plain")
    """
    raise NotImplementedError("TODO: implement chat() — start with the non-streaming version")

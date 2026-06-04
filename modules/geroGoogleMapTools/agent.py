"""OpenAI agent loop with Google Maps tool dispatch."""

import json
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall
from googlemaps_tools import TOOLS, TOOL_REGISTRY

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are a navigation and location assistant embedded in a host robot \
at Charles de Gaulle Airport (CDG), Paris, France.

Your job is to help passengers and staff find facilities, plan routes, and answer \
location-based questions using real Google Maps data. Always call a tool to get \
up-to-date information — never invent addresses, distances, or directions.

The robot is physically stationed at Terminal 2F, CDG Roissy (lat 49.0052, lng 2.5770). \
This is the default origin for all searches and routes unless the user specifies otherwise. \
Never ask the user for coordinates — resolve locations by name using geocode_address.

Guidelines:
- When the user asks "where is X", "find me X", or "I'm looking for X", use search_places_text \
  or search_nearby_places with the robot's default position. This includes hotels, transport, shops.
- When asked for directions to a named place, call geocode_address to get its coordinates \
  then call compute_route from the robot's default position.
- When asked "what is closest", use compute_route_matrix from the robot's position \
  to compare multiple candidates.
- When more detail is needed (hours, accessibility, phone), call get_place_details \
  with the place_id from the search result.
- Use WALK travel mode by default.
- Format distances in metres or kilometres. Format durations as minutes and seconds.
- If a tool returns an error, report it clearly and do not guess.
- Keep answers concise. Use bullet points for lists of places or steps.
"""


def run_turn(client: OpenAI, messages: list, user_input: str) -> str:
    """Process one user turn, dispatching tools as needed. Returns the final assistant reply."""
    messages.append({"role": "user", "content": user_input})
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")

    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        message = choice.message
        messages.append(message)

        if choice.finish_reason == "stop":
            return message.content or ""

        if choice.finish_reason == "tool_calls":
            for tool_call in (message.tool_calls or []):
                if not isinstance(tool_call, ChatCompletionMessageToolCall):
                    continue
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                    fn = TOOL_REGISTRY.get(name)
                    if fn is None:
                        result = {"error": f"Unknown tool: {name}"}
                    else:
                        result = fn(**args)
                except Exception as e:
                    result = {"error": str(e)}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

    return "Could not complete the request within the maximum number of steps."

"""OpenAI agent loop with Airlabs tool dispatch."""

import json
import os
from openai import OpenAI
from airlabs_tools import TOOLS, TOOL_REGISTRY

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are a helpful flight information assistant specialised in \
Charles de Gaulle Airport (CDG), Paris, France.

When answering questions about CDG or any other airport, use the available tools \
to retrieve live and up-to-date information. Do not make up flight numbers, times, \
or status — always call a tool first.

Guidelines:
- Default to CDG (IATA code: CDG) when the user does not specify an airport.
- When the user asks about 'departures' or 'flights leaving', use get_departures or \
get_live_flights_for_airport with direction='departures'.
- When the user asks about 'arrivals' or 'flights landing', use get_arrivals or \
get_live_flights_for_airport with direction='arrivals'.
- When the user mentions a specific flight number (e.g. 'AF447'), use get_flight_status.
- For delay questions, use get_delayed_flights; default to checking departures unless \
the user says 'arrivals'.
- You may call multiple tools in a single response if the question requires combining \
information (e.g. delayed departures + airline details).
- Format flight times in a human-readable way (e.g. '14:35 local').
- If a tool returns an error, tell the user clearly and do not guess an answer.
- Keep responses concise and structured. Use bullet points or short tables for lists of flights.
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
            for tool_call in message.tool_calls:
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

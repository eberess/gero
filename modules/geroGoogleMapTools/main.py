"""CLI entry point for the CDG Maps Assistant."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from agent import SYSTEM_PROMPT, run_turn


def _validate_env() -> None:
    missing = [k for k in ("GOOGLE_MAPS_API_KEY", "OPENAI_API_KEY") if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def main() -> None:
    load_dotenv()
    _validate_env()

    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("CDG Maps Assistant — type 'exit' to quit.")
    print("Ask anything about locations, routes, or facilities at Charles de Gaulle Airport.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Goodbye.")
            break

        answer = run_turn(client, messages, user_input)
        print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    main()

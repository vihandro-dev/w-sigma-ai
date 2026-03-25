#!/usr/bin/env python3
"""Terminal version of the Gen Alpha chatbot."""

from chat import send_message

def main():
    print("\n" + "=" * 50)
    print("  W_Sigma.ai - ur gen alpha ai bestie 🔥")
    print("=" * 50)
    print("  type 'quit' to dip out")
    print("=" * 50 + "\n")

    username = input("  whats ur name? > ").strip()
    if not username:
        username = "anon"

    print(f"\n  aight {username}, lets gooo 💀\n")

    while True:
        try:
            user_input = input(f"  {username}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  W_Sigma.ai: aight bet, see u later fr fr 👋\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("\n  W_Sigma.ai: aight bet, see u later fr fr 👋\n")
            break

        try:
            reply = send_message(username, user_input)
            print(f"\n  W_Sigma.ai: {reply}\n")
        except Exception as e:
            print(f"\n  [error: {e}]\n")


if __name__ == "__main__":
    main()

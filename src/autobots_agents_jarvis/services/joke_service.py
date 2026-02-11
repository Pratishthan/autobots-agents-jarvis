# ABOUTME: Joke service — mock implementation for demonstration purposes.
# ABOUTME: Provides hardcoded jokes in different categories.

import random
from typing import Any

# Mock joke database
JOKES: dict[str, list[dict[str, Any]]] = {
    "programming": [
        {
            "joke_text": "Why do programmers prefer dark mode? Because light attracts bugs!",
            "category": "programming",
            "rating": 4,
        },
        {
            "joke_text": "How many programmers does it take to change a light bulb? None, it's a hardware problem!",
            "category": "programming",
            "rating": 3,
        },
        {
            "joke_text": "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
            "category": "programming",
            "rating": 5,
        },
        {
            "joke_text": "There are 10 types of people in the world: those who understand binary and those who don't.",
            "category": "programming",
            "rating": 4,
        },
        {
            "joke_text": "Why do Python programmers wear glasses? Because they can't C!",
            "category": "programming",
            "rating": 3,
        },
    ],
    "general": [
        {
            "joke_text": "Why don't scientists trust atoms? Because they make up everything!",
            "category": "general",
            "rating": 4,
        },
        {
            "joke_text": "What do you call a fake noodle? An impasta!",
            "category": "general",
            "rating": 3,
        },
        {
            "joke_text": "Why did the scarecrow win an award? He was outstanding in his field!",
            "category": "general",
            "rating": 3,
        },
    ],
    "knock-knock": [
        {
            "joke_text": "Knock knock. Who's there? Interrupting cow. Interrupting cow w— MOOOOO!",
            "category": "knock-knock",
            "rating": 2,
        },
        {
            "joke_text": "Knock knock. Who's there? Tank. Tank who? You're welcome!",
            "category": "knock-knock",
            "rating": 3,
        },
    ],
    "dad-joke": [
        {
            "joke_text": "I'm afraid for the calendar. Its days are numbered.",
            "category": "dad-joke",
            "rating": 4,
        },
        {
            "joke_text": "What do you call a bear with no teeth? A gummy bear!",
            "category": "dad-joke",
            "rating": 3,
        },
        {
            "joke_text": "Why don't eggs tell jokes? They'd crack each other up!",
            "category": "dad-joke",
            "rating": 3,
        },
        {
            "joke_text": "I used to hate facial hair, but then it grew on me.",
            "category": "dad-joke",
            "rating": 4,
        },
    ],
}


def get_joke(category: str) -> dict[str, Any]:
    """Get a random joke from the specified category.

    Args:
        category: The joke category (programming, general, knock-knock, dad-joke)

    Returns:
        A dictionary containing joke_text, category, and rating
    """
    if category not in JOKES:
        return {"error": f"Invalid category '{category}'. Use get_joke_categories to see available categories."}

    return random.choice(JOKES[category])


def list_categories() -> list[str]:
    """Get the list of available joke categories.

    Returns:
        List of available category names
    """
    return list(JOKES.keys())

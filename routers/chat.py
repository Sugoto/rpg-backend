from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from openai import OpenAI
import random
from constants.prompts import BASE_PROMPT, PLOT_0

router = APIRouter(tags=["Chat"])

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class ChatInput(BaseModel):
    message: str


from typing import Optional


class DiceRoll(BaseModel):
    dice_type: str
    rolls: List[int]
    total: int


class ChatOutput(BaseModel):
    response: str


# Dice roll functions
def roll_d4():
    return random.randint(1, 4)


def roll_d6():
    return random.randint(1, 6)


def roll_d8():
    return random.randint(1, 8)


def roll_d10():
    return random.randint(1, 10)


def roll_d12():
    return random.randint(1, 12)


def roll_d20():
    return random.randint(1, 20)


def roll_dice(dice_type: str, num_dice: int = 1):
    dice_functions = {
        "d4": roll_d4,
        "d6": roll_d6,
        "d8": roll_d8,
        "d10": roll_d10,
        "d12": roll_d12,
        "d20": roll_d20,
    }

    if dice_type not in dice_functions:
        raise ValueError(f"Invalid dice type: {dice_type}")

    results = [dice_functions[dice_type]() for _ in range(num_dice)]
    return {"dice_type": dice_type, "rolls": results, "total": sum(results)}


# OpenAI function definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Roll one or more dice of a specified type",
            "parameters": {
                "type": "object",
                "properties": {
                    "dice_type": {
                        "type": "string",
                        "enum": ["d4", "d6", "d8", "d10", "d12", "d20"],
                        "description": "The type of dice to roll",
                    },
                    "num_dice": {
                        "type": "integer",
                        "default": 1,
                        "description": "The number of dice to roll",
                    },
                },
                "required": ["dice_type"],
            },
        },
    }
]


@router.post("/chat", response_model=ChatOutput)
async def chat(input: ChatInput):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": BASE_PROMPT + PLOT_0,
                },
                {"role": "user", "content": input.message},
            ],
            tools=tools,
        )

        assistant_message = response.choices[0].message
        content = assistant_message.content or ""
        dice_rolls = []

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                if tool_call.function.name == "roll_dice":
                    args = json.loads(tool_call.function.arguments)
                    dice_type = args.get("dice_type")
                    num_dice = args.get("num_dice", 1)

                    roll_result = roll_dice(dice_type, num_dice)
                    dice_rolls.append(roll_result)

                    roll_description = f"Rolled {num_dice}{dice_type}: {roll_result['rolls']} (Total: {roll_result['total']})"
                    print(roll_description)
                    content += f"\n\nDice Roll: {roll_description}"

            messages = [
                {
                    "role": "system",
                    "content": "You are a Dungeon Master in a D&D-inspired RPG. Use function calling for dice rolls when appropriate.",
                },
                {"role": "user", "content": input.message},
                assistant_message,
            ]

            for tool_call, roll_result in zip(assistant_message.tool_calls, dice_rolls):
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(roll_result),
                        "tool_call_id": tool_call.id,
                    }
                )

            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            content = final_response.choices[0].message.content or ""

        return ChatOutput(response=content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

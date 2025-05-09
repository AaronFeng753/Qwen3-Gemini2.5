"""
title: Qwen3-Gemini2.5
author: AaronFeng753
author_url: https://github.com/AaronFeng753
funding_url: https://github.com/AaronFeng753
version: 0.1
"""

from pydantic import BaseModel, Field
from typing import Optional
import re


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        max_turns: int = Field(
            default=99999,
            description="Maximum allowable conversation turns for a user.",
        )
        pass

    class UserValves(BaseModel):
        max_turns: int = Field(
            default=99999,
            description="Maximum allowable conversation turns for a user.",
        )
        pass

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        # self.file_handler = True

        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,
        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.

        messages = body.get("messages", [])
        modified_messages = []

        for message in messages:
            if message.get("role") == "assistant":
                message_content = message.get("content", "")
                pattern = r"<details[^>]*>.*?</details>"
                modified_content = re.sub(pattern, "", message_content, flags=re.DOTALL)
                modified_message = {"role": "assistant", "content": modified_content}
            else:
                modified_message = message
            modified_messages.append(modified_message)

        body["messages"] = modified_messages

        assistant_message = {
            "role": "assistant",
            "content": "<think>\nMy step by step thinking process went something like this:\n1. ",
        }
        body["messages"].append(assistant_message)

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.

        messages = body.get("messages", [])
        if not messages:
            return body

        model_response = messages[-1].get("content", "")

        model_response = (
            f"<details>\n<summary>Thoughts 💭</summary>\nMy step by step thinking process went something like this:\n1. "
            + model_response
        )

        model_response = model_response.replace(
            "</think>",
            "\n\n---\n\n\\[\n\\boxed{END-OF-Thoughts}\n\\]\n\n---\n\n</details>",
        )

        messages[-1]["content"] = model_response
        body["messages"] = messages

        return body

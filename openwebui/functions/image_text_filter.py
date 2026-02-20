"""
title: image_text_filter
author: open-webui
author_url: Brian Fehrman
version: 0.4
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def has_image_files(self, files: list) -> bool:
        return any(
            f.get("type") == "file"
            and f.get("file", {})
            .get("meta", {})
            .get("content_type", "")
            .startswith("image/")
            for f in (files or [])
        )

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        response_message = "Respond only with: Please provide an image for processing"
        image_placeholder = "Please process this image."

        messages = body.get("messages", [])
        if not messages:
            return body

        # Determine if the last user message has an image attached
        metadata = body.get("metadata", {})
        parent_message = metadata.get("parent_message", {})
        parent_files = parent_message.get("files", []) or []
        last_has_image = self.has_image_files(parent_files)

        cleaned_messages = []
        for i, msg in enumerate(messages):
            msg = msg.copy()
            is_last = i == len(messages) - 1
            role = msg.get("role", "")

            if role == "user":
                content = msg.get("content", "")
                if is_last:
                    if last_has_image:
                        # Image present: set a non-blank placeholder so Bedrock accepts it
                        # OpenWebUI will inject the actual image separately
                        msg["content"] = image_placeholder
                    else:
                        # No image: prompt the user to provide one
                        msg["content"] = response_message
                else:
                    # Prior user messages: if blank, set a safe placeholder
                    if not content or not content.strip():
                        msg["content"] = image_placeholder

            cleaned_messages.append(msg)

        body = {**body, "messages": cleaned_messages}
        print(f"inlet:cleaned_messages:{cleaned_messages}")
        return body

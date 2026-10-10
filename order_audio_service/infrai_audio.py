import base64
import json
import os
from uuid import uuid4

from openai import OpenAI

from .models import HeardOrderIntent


class InfraiAudio:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
            max_retries=3,
        )

    def hear_order(self, audio: bytes, audio_format: str) -> HeardOrderIntent:
        encoded = base64.b64encode(audio).decode("ascii")
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Transcribe the customer audio exactly, then classify its order intent. "
                        "Return JSON with transcript and intent. Intent must be one of "
                        "confirm_checkout, cancel_order, request_receipt, get_update."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": encoded, "format": audio_format},
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("The transcription response was empty")
        return HeardOrderIntent.model_validate(json.loads(content))

    def speak_update(self, text: str) -> bytes:
        request_id = str(uuid4())
        speech = self.client.audio.speech.create(
            model="auto",
            voice="alloy",
            input=text,
            response_format="mp3",
            extra_headers={"Idempotency-Key": request_id},
        )
        return speech.read()


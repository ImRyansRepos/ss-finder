
# openai_client.py

import base64
from pathlib import Path
from typing import List

from openai import OpenAI
from config import OPENAI_API_KEY


class OpenAIClient:
    """
    Thin wrapper around OpenAI client for vision captioning and embeddings.
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    @staticmethod
    def _encode_image_to_data_url(image_path: str) -> str:
        """
        Encode a local image file as a data URL suitable for the vision model.
        """
        path = Path(image_path)
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

        with path.open("rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime};base64,{b64}"

    def caption_image(self, image_path: str) -> str:
        """
        Generate a short caption for an image for search purposes.
        """
        data_url = self._encode_image_to_data_url(image_path)

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Describe this image briefly in one short sentence. "
                                "Focus on what a person might remember about it for search."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
            max_tokens=64,
        )

        caption = response.choices[0].message.content
        return caption.strip()

    def embed_text(self, text: str) -> List[float]:
        """
        Create an embedding vector for the given text.
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

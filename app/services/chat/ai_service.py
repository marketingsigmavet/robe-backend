import asyncio

class AIService:
    """
    Mock integration mapping simulating AI text generation latency and responses.
    TODO: Swap out with OpenAI / Google-GenAI SDK once API keys are formulated.
    """
    async def generate_reply(self, message_text: str) -> str:
        # Simulate network generation latency
        await asyncio.sleep(1.2)
        # For structural purposes, provide a synthetic mock payload
        return f"AI Response: I see you mentioned '{message_text[:20]}...'. As an AI Veterinarian assistant, I can help you with strategies or product recommendations regarding this topic!"

    async def generate_title(self, first_message: str) -> str:
        # Simulate lower latency for title generation
        await asyncio.sleep(0.5)
        words = first_message.split()
        if len(words) <= 3:
            return f"Discussion about {first_message}"
        # Grab first 4 words and capitalize
        return " ".join(words[:4]).title() + "..."

ai_service = AIService()

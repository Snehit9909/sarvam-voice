import boto3
import json
from config.config import AWS_REGION, BEDROCK_MODEL_ID

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

SYSTEM_PROMPT_TEXT = """
You are a real-time conversational voice assistant.

You speak naturally, like a human in a live conversation.
Your tone should sound friendly, confident, and engaging,
but you must NEVER describe your tone or emotions in words.

Rules:
- Do NOT include stage directions like *cheerful*, *friendly*, *engaged tone*, or anything in brackets or asterisks
- Speak naturally without narrating how you sound
- Never say you are an AI unless explicitly asked
- Keep responses conversational and concise (1–3 sentences)
- Use simple, spoken English
- Respond as if the user is talking to you live
- Do not repeat the user’s question verbatim
- If the user says thanks, respond briefly and naturally
"""

conversation = []

def call_llm(user_text):
    conversation.append({
        "role": "user",
        "content": user_text
    })

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": SYSTEM_PROMPT_TEXT, 
        "messages": conversation,
        "max_tokens": 200,
        "temperature": 0.5
    }

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        
        # Accessing the response text
        reply = result["content"][0]["text"]

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        print(f"🤖 Assistant: {reply}")
        return reply

    except Exception as e:
        print(f"❌ Bedrock LLM Error: {e}")
        # Return a string so the TTS has something to say
        return "I am sorry, I am having trouble connecting to my brain."

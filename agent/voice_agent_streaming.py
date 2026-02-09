from strands import Agent
from strands.models.bedrock import BedrockModel
from config.config import AWS_REGION, BEDROCK_MODEL_ID

model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    region_name=AWS_REGION,
    temperature=0.3,
    max_tokens=200
)


agent = Agent(
    model=model,
    system_prompt=(
        "You are a concise English-only voice assistant. "
        "Strictly reply in English. If the user speaks another language, "
        "politely ask them to speak in English. "
        "Keep your response to one short sentence."
    )
)

def run_agent(prompt: str) -> str:
    result = agent(prompt)
    return str(result).strip()


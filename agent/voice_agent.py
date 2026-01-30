from strands import Agent
from strands.models.bedrock import BedrockModel
from config.config import AWS_REGION, BEDROCK_MODEL_ID

model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    region_name=AWS_REGION,
    temperature=0.3,
    max_tokens=40
)

agent = Agent(
    model=model,
    system_prompt="You are a brief voice assistant. Reply in one short sentence."
)

def run_agent(text: str) -> str:
    return str(agent(text)).strip()

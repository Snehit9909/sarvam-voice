from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent() # Your agent configuration here

@app.entrypoint
def invoke(payload):
    """The main entry point called by AgentCore Runtime"""
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()

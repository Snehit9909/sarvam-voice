import boto3

class BedrockLLM:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime")

    def generate(self, text):
        response = self.client.invoke_model(
            modelId="anthropic.claude-3-sonnet",
            body={
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 200
            }
        )
        return response["output"]["message"]["content"][0]["text"]

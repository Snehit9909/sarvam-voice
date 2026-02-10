import boto3
import json
import os
from config.config import CURRENT_AGENT_ARN
client = boto3.client(
    "bedrock-agentcore",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

def run_agent(user_input: str, session_id: str) -> str:
    target_arn = os.getenv("AGENT_RUNTIME_ARN", CURRENT_AGENT_ARN)
    qualifier = os.getenv("AGENT_QUALIFIER", "DEFAULT")
    payload = {"prompt": user_input}

    try:
        print(f"[DEBUG] Invoking Agent: {target_arn} | Session: {session_id}", flush=True)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=target_arn,
            qualifier=qualifier,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
            contentType="application/json",
            accept="application/json"
        )

        raw_body = response["response"].read().decode("utf-8")
        data = json.loads(raw_body)
        print(f"[DEBUG] Raw Agent Data: {data}", flush=True)

        result = data.get("result", {})
        content_list = result.get("content", [])

        if content_list and isinstance(content_list, list):
            # Extract text from the first item in the content list
            text = content_list[0].get("text", "")
        else:
            # Fallback for other response formats
            text = data.get("message") or data.get("output") or ""

        # Ensure we return a clean string, not a dictionary
        return str(text).strip() if text else "I'm sorry, I couldn't generate a response."

    except Exception as e:
        print(f"[ERROR] AgentCore invocation failed: {e}", flush=True)
        return "I'm having trouble connecting to my brain right now."


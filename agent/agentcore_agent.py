import boto3
import json
import os
import uuid

client = boto3.client(
    "bedrock-agentcore",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

AGENT_RUNTIME_ARN = os.getenv("AGENT_RUNTIME_ARN")
QUALIFIER = os.getenv("AGENT_QUALIFIER", "DEFAULT")


def run_agent(user_input: str) -> str:
    session_id = str(uuid.uuid4())

    payload = {
        "prompt": user_input   
    }

    try:
        print("[DEBUG] Invoking AgentCore...", flush=True)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            qualifier=QUALIFIER,
            runtimeSessionId=session_id,
            payload=json.dumps(payload).encode("utf-8"),
            contentType="application/json",
            accept="application/json"
        )

        raw_body = response["response"].read().decode("utf-8")
        print("[DEBUG] Raw response:", raw_body, flush=True)

        data = json.loads(raw_body)

        # Your agent returns either of these
        text = (
            data.get("message")     
            or data.get("result")
            or data.get("completion")
            or data.get("output")
            or ""
        )

        return text.strip()


    except Exception as e:
        print(f"[ERROR] AgentCore invocation failed: {e}", flush=True)
        return ""

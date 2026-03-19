# ======================================================
# 書き換えるのはこの2行だけです！
# ======================================================
PARK_NAME = "サンリオピューロランド"   # ← 自分のパーク名に変更
PARK_URL  = "https://www.puroland.jp/"  # ← 自分のパークURLに変更
# ======================================================

import os
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from datetime import datetime

REGION    = "us-west-2"
MEMORY_ID = os.environ.get("MEMORY_ID", "")
ACTOR_ID  = "handson-user-01"

browser_tool = AgentCoreBrowser(region=REGION)

SYSTEM_PROMPT = f"""あなたは「{PARK_NAME}」専任の案内エージェントです。
本日の日付: {datetime.now().strftime('%Y年%m月%d日')}

## ルール
- 必ず公式サイト（{PARK_URL}）にアクセスして最新情報を取得すること
- 回答の末尾に「（{PARK_NAME} 公式サイトより）」と出典を書くこと
- 情報が見つからない場合は正直に伝え、公式サイトのURLを案内すること
"""

app = BedrockAgentCoreApp(debug=True)

@app.entrypoint
def invoke(payload: dict) -> dict:
    user_message = payload.get("prompt", "こんにちは")
    session_id = payload.get("sessionId", f"session-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    if MEMORY_ID:
        config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=ACTOR_ID
        )
        session_manager = AgentCoreMemorySessionManager(config, region_name=REGION)
        agent = Agent(
            system_prompt=SYSTEM_PROMPT,
            tools=[browser_tool.browser],
            model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            session_manager=session_manager
        )
        result = agent(user_message)
        session_manager.close()
    else:
        agent = Agent(
            system_prompt=SYSTEM_PROMPT,
            tools=[browser_tool.browser],
            model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )
        result = agent(user_message)

    text_parts = [b["text"] for b in result.message.get("content", []) if "text" in b]
    return {
        "result": "\n".join(text_parts) if text_parts else str(result),
        "sessionId": session_id
    }

if __name__ == "__main__":
    app.run()


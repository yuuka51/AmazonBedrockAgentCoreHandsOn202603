import boto3, json, time
from bedrock_agentcore.memory import MemoryClient

REGION = "us-west-2"

# 1. IAMロール作成
iam = boto3.client("iam")
sts = boto3.client("sts", region_name=REGION)
account_id = sts.get_caller_identity()["Account"]
role_name = "AgentCoreMemoryExecutionRole"

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    role = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="AgentCore Memory execution role"
    )
    role_arn = role["Role"]["Arn"]
    print("✅ IAMロールを作成しました")
except iam.exceptions.EntityAlreadyExistsException:
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    print("ℹ️  IAMロールはすでに存在します")

iam.put_role_policy(
    RoleName=role_name,
    PolicyName="BedrockInvokePolicy",
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            "Resource": "*"
        }]
    })
)
print("✅ Bedrockアクセス権限を付与しました")
print("⏳ IAMロールの反映を待っています（10秒）...")
time.sleep(10)

# 2. Memoryリソース作成
print("🧠 Memoryリソースを作成しています（1〜2分かかります）...")
client = MemoryClient(region_name=REGION)
memory = client.create_memory_and_wait(
    name="ParkGuideMemory",
    description="テーマパーク案内エージェントの会話記憶",
    strategies=[
        {
            "summaryMemoryStrategy": {
                "name": "SessionSummarizer",
                "namespaces": ["/summaries/{actorId}/{sessionId}/"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name": "PreferenceLearner",
                "namespaces": ["/preferences/{actorId}/"]
            }
        }
    ],
    memory_execution_role_arn=role_arn
)

memory_id = memory.get("id")
print(f"\n✅ セットアップ完了！")
print(f"以下のコマンドを実行してください：")
print(f"\nexport MEMORY_ID={memory_id}")


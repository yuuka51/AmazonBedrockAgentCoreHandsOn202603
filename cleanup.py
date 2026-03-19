import boto3
from bedrock_agentcore.memory import MemoryClient

REGION = "us-west-2"

# Memoryリソースの削除
client = MemoryClient(region_name=REGION)
memories = client.list_memories()
for m in memories:
    print(f"🗑️  Memoryリソースを削除中: {m['id']}...")
    client.delete_memory(memory_id=m["id"])
    print(f"✅ 削除しました: {m['id']}")

if not memories:
    print("ℹ️  削除対象の Memory リソースはありません")

# IAMロールの削除
iam = boto3.client("iam")
role_name = "AgentCoreMemoryExecutionRole"
try:
    iam.delete_role_policy(RoleName=role_name, PolicyName="BedrockInvokePolicy")
    iam.delete_role(RoleName=role_name)
    print(f"✅ IAMロール {role_name} を削除しました")
except iam.exceptions.NoSuchEntityException:
    print("ℹ️  IAMロールは存在しません（削除済み）")

print("\n🧹 クリーンアップ完了！")


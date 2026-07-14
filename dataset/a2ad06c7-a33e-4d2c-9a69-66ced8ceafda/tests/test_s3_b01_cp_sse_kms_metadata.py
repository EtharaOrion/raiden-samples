import uuid
import pytest


def test_cp_with_sse_kms_stores_encryption_metadata(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "kms.bin"
    payload = b"encrypted-payload"
    src.write_bytes(payload)
    kms_key = "foo"

    result = cli(
        "s3", "cp", str(src), f"s3://{bucket}/kms.bin",
        "--sse", "aws:kms", "--sse-kms-key-id", kms_key,
    )
    assert result.returncode == 0, result.stderr

    head = s3_client.head_object(Bucket=bucket, Key="kms.bin")
    assert head.get("ServerSideEncryption") == "aws:kms"
    body = s3_client.get_object(Bucket=bucket, Key="kms.bin")["Body"].read()
    assert body == payload

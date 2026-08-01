import uuid
import pytest


def test_cp_sse_kms_stores_encryption_metadata(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "secret.bin"
    payload = b"encrypted-bytes"
    src.write_bytes(payload)
    key_id = "foo"

    result = cli(
        "s3", "cp", str(src), f"s3://{bucket}/secret.bin",
        "--sse", "aws:kms", "--sse-kms-key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    head = s3_client.head_object(Bucket=bucket, Key="secret.bin")
    assert head.get("ServerSideEncryption") == "aws:kms"
    assert s3_client.get_object(Bucket=bucket, Key="secret.bin")["Body"].read() == payload

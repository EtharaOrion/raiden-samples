

import uuid


def test_workflow_rb_nonempty_fails_then_force(cli, s3_client, tmp_path):
    bucket = f"test-rbneg-{uuid.uuid4().hex[:12]}"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    f = tmp_path / "data.bin"
    f.write_bytes(b"keepme")
    r = cli("s3", "cp", str(f), f"s3://{bucket}/data.bin")
    assert r.returncode == 0

    assert s3_client.get_object(Bucket=bucket, Key="data.bin")["Body"].read() == b"keepme"

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode != 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets
    s3_client.head_object(Bucket=bucket, Key="data.bin")

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets

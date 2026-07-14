

import uuid


def test_workflow_mv_local_to_s3_then_negative_self_mv(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    local = tmp_path / "local.txt"
    payload = b"move-me-please"
    local.write_bytes(payload)

    r = cli("s3", "mv", str(local), f"s3://{bucket}/k1.txt")
    assert r.returncode == 0

    assert not local.exists()
    got = s3_client.get_object(Bucket=bucket, Key="k1.txt")["Body"].read()
    assert got == payload

    r = cli("s3", "mv", f"s3://{bucket}/k1.txt", f"s3://{bucket}/k1.txt")
    assert r.returncode != 0
    stderr = r.stderr.decode() if isinstance(r.stderr, bytes) else r.stderr
    assert stderr

    got = s3_client.get_object(Bucket=bucket, Key="k1.txt")["Body"].read()
    assert got == payload

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets

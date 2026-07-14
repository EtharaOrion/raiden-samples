

import uuid


def test_workflow_mb_cp_roundtrip_rb(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    src = tmp_path / "src.bin"
    payload = b"hello-roundtrip-\x00\x01\x02" * 100
    src.write_bytes(payload)

    r = cli("s3", "cp", str(src), f"s3://{bucket}/data/key.bin")
    assert r.returncode == 0

    got = s3_client.get_object(Bucket=bucket, Key="data/key.bin")["Body"].read()
    assert got == payload

    dst = tmp_path / "dst.bin"
    r = cli("s3", "cp", f"s3://{bucket}/data/key.bin", str(dst))
    assert r.returncode == 0
    assert dst.read_bytes() == payload

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode != 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets

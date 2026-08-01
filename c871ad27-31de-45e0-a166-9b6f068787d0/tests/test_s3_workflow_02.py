


def test_workflow_mv_local_to_s3_then_negative_self_mv(cli, s3_client, tmp_path):
    bucket = "test-mv-negative-bucket"
    s3_client.create_bucket(Bucket=bucket)

    local = tmp_path / "tomove.txt"
    payload = b"move-me-please"
    local.write_bytes(payload)

    r = cli("s3", "mv", str(local), f"s3://{bucket}/tomove.txt")
    assert r.returncode == 0
    assert not local.exists()

    obj = s3_client.get_object(Bucket=bucket, Key="tomove.txt")
    assert obj["Body"].read() == payload

    r = cli("s3", "mv", f"s3://{bucket}/tomove.txt", f"s3://{bucket}/tomove.txt")
    assert r.returncode != 0

    obj = s3_client.get_object(Bucket=bucket, Key="tomove.txt")
    assert obj["Body"].read() == payload

    back = tmp_path / "back.txt"
    r = cli("s3", "cp", f"s3://{bucket}/tomove.txt", str(back))
    assert r.returncode == 0
    assert back.read_bytes() == payload

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets

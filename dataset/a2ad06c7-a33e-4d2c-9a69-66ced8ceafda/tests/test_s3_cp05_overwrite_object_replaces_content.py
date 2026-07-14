import uuid


def test_cp05_overwrite_object_replaces_content(cli, s3_client, tmp_path):
    """Re-uploading to same key replaces content fully (no partial merge)."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    key = "k"
    src1 = tmp_path / "v1"
    src1.write_bytes(b"old")
    src2 = tmp_path / "v2"
    src2.write_bytes(b"newer-and-longer")
    r1 = cli("s3", "cp", str(src1), f"s3://{bucket}/{key}")
    assert r1.returncode == 0, r1.stderr
    r2 = cli("s3", "cp", str(src2), f"s3://{bucket}/{key}")
    assert r2.returncode == 0, r2.stderr
    head = s3_client.head_object(Bucket=bucket, Key=key)
    assert head["ContentLength"] == 16
    body = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
    assert body == b"newer-and-longer"

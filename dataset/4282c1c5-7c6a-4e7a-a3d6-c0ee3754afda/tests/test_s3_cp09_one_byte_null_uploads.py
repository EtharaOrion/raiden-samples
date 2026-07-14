import uuid


def test_cp09_one_byte_null_uploads(cli, s3_client, tmp_path):
    """1-byte null payload uploads and roundtrips exactly."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "null"
    src.write_bytes(b"\x00")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/null")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="null")
    assert head["ContentLength"] == 1
    body = s3_client.get_object(Bucket=bucket, Key="null")["Body"].read()
    assert body == b"\x00"

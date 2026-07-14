import uuid


def test_sync_uploaded_objects_bytes_match_source(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    pa = b"first-payload-bytes-AAA"
    pb = b"second-different-payload-BBB-bytes"
    (src_dir / "a.bin").write_bytes(pa)
    (src_dir / "b.bin").write_bytes(pb)

    result = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert result.returncode == 0, result.stderr

    body_a = s3_client.get_object(Bucket=bucket, Key="a.bin")["Body"].read()
    body_b = s3_client.get_object(Bucket=bucket, Key="b.bin")["Body"].read()
    assert body_a == pa
    assert body_b == pb

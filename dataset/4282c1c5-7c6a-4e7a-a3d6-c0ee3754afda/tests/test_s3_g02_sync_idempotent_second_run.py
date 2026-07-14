import uuid


def test_sync_second_run_unchanged_pair_is_noop(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_bytes(b"alpha")
    (src_dir / "b.txt").write_bytes(b"beta")

    r1 = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r1.returncode == 0, r1.stderr

    head_a = s3_client.head_object(Bucket=bucket, Key="a.txt")
    head_b = s3_client.head_object(Bucket=bucket, Key="b.txt")
    etag_a, lm_a = head_a["ETag"], head_a["LastModified"]
    etag_b, lm_b = head_b["ETag"], head_b["LastModified"]

    r2 = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r2.returncode == 0, r2.stderr

    head_a2 = s3_client.head_object(Bucket=bucket, Key="a.txt")
    head_b2 = s3_client.head_object(Bucket=bucket, Key="b.txt")
    assert head_a2["ETag"] == etag_a
    assert head_b2["ETag"] == etag_b
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert {"a.txt", "b.txt"} <= keys
    assert s3_client.get_object(Bucket=bucket, Key="a.txt")["Body"].read() == b"alpha"
    assert s3_client.get_object(Bucket=bucket, Key="b.txt")["Body"].read() == b"beta"

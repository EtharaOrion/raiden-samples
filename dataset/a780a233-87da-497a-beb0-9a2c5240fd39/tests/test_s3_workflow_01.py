from _s3_http import S3HTTPError as ClientError


import uuid


def test_workflow_sync_then_mv(cli, s3_client, tmp_path):
    bucket = f"test-bucket-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    files = {
        "a.txt": b"alpha-content",
        "b.txt": b"beta-content-data",
        "nested/c.txt": b"gamma-nested-bytes",
    }
    for rel, data in files.items():
        p = src_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    result = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert result.returncode == 0

    listed = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {obj["Key"] for obj in listed}
    assert keys >= set(files.keys())
    for rel, data in files.items():
        body = s3_client.get_object(Bucket=bucket, Key=rel)["Body"].read()
        assert body == data

    result = cli("s3", "mv", f"s3://{bucket}/a.txt", f"s3://{bucket}/moved/a.txt")
    assert result.returncode == 0

    try:
        s3_client.head_object(Bucket=bucket, Key="a.txt")
        raise AssertionError("a.txt should have been moved")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    moved_body = s3_client.get_object(Bucket=bucket, Key="moved/a.txt")["Body"].read()
    assert moved_body == files["a.txt"]

    out_file = tmp_path / "downloaded_b.txt"
    result = cli("s3", "mv", f"s3://{bucket}/b.txt", str(out_file))
    assert result.returncode == 0
    assert out_file.read_bytes() == files["b.txt"]
    try:
        s3_client.head_object(Bucket=bucket, Key="b.txt")
        raise AssertionError("b.txt should have been moved off S3")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

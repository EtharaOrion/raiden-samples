from _s3_http import S3HTTPError as ClientError


def test_workflow_rb_nonempty_fails_then_force_succeeds(cli, s3_client, tmp_path):
    bucket = "test-nonempty-bucket-xyz123"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    src = tmp_path / "src"
    src.mkdir()
    (src / "keep.txt").write_bytes(b"keep-me")
    (src / "also.txt").write_bytes(b"also-me")

    r = cli("s3", "sync", str(src), f"s3://{bucket}")
    assert r.returncode == 0

    keys_before = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert {"keep.txt", "also.txt"}.issubset(keys_before)

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode != 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets
    keys_after = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert keys_after == keys_before

    r = cli("s3", "rm", f"s3://{bucket}/keep.txt")
    assert r.returncode == 0

    try:
        s3_client.head_object(Bucket=bucket, Key="keep.txt")
        raise AssertionError()
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets

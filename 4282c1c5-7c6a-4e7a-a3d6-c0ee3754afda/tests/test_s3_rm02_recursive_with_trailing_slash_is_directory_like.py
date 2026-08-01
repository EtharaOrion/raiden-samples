import uuid


def test_rm02_recursive_with_trailing_slash_is_directory_like(cli, s3_client, tmp_path):
    """rm s3://b/foo/ --recursive: only foo/baz deleted; foobar and foo.txt survive."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    for k in ("foobar", "foo.txt", "foo/baz"):
        s3_client.put_object(Bucket=bucket, Key=k, Body=b"x")
    r = cli("s3", "rm", f"s3://{bucket}/foo/", "--recursive")
    assert r.returncode == 0, r.stderr
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "foo/baz" not in keys, f"foo/baz should be gone; got {keys}"
    assert "foobar" in keys, f"foobar should survive trailing-slash prefix; got {keys}"
    assert "foo.txt" in keys, f"foo.txt should survive trailing-slash prefix; got {keys}"

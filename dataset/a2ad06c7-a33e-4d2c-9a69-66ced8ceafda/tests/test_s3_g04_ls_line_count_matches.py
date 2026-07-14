import uuid


def test_ls_recursive_line_count_matches_object_count(cli, s3_client):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    keys = ["a.txt", "b.txt", "c.txt"]
    for k in keys:
        s3_client.put_object(Bucket=bucket, Key=k, Body=b"x")

    result = cli("s3", "ls", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0, result.stderr
    for k in keys:
        assert k in result.stdout

    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) == len(keys)

import uuid


def test_ls_empty_bucket_exits_zero_after_cli_mb(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    r_mb = cli("s3", "mb", f"s3://{bucket}")
    assert r_mb.returncode == 0, r_mb.stderr
    names = {b["Name"] for b in s3_client.list_buckets().get("Buckets", [])}
    assert bucket in names

    result = cli("s3", "ls", f"s3://{bucket}/")
    assert result.returncode == 0, result.stderr

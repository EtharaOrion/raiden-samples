import uuid


def test_cp06_download_truncates_existing_local(cli, s3_client, tmp_path):
    """Download onto pre-existing larger local file fully replaces (truncates)."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="k", Body=b"short")
    local = tmp_path / "local.bin"
    local.write_bytes(b"X" * 1000)
    r = cli("s3", "cp", f"s3://{bucket}/k", str(local))
    assert r.returncode == 0, r.stderr
    assert local.read_bytes() == b"short", "download did not truncate existing larger file"

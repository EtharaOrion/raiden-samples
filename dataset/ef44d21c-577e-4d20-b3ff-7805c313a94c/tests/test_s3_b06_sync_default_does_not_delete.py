import uuid


def test_sync_default_does_not_delete_destination_extras(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="leftover.txt", Body=b"keep-me")

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "new.txt").write_bytes(b"fresh")

    result = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert result.returncode == 0, result.stderr

    assert s3_client.get_object(Bucket=bucket, Key="leftover.txt")["Body"].read() == b"keep-me"
    assert s3_client.get_object(Bucket=bucket, Key="new.txt")["Body"].read() == b"fresh"

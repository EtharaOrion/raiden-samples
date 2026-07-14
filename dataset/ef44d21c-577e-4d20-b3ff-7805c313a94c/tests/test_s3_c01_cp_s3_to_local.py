import uuid


def test_cp_s3_to_local_writes_bytes_to_path(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = b"download-content"
    s3_client.put_object(Bucket=bucket, Key="src.bin", Body=payload)

    dest = tmp_path / "out.bin"
    result = cli("s3", "cp", f"s3://{bucket}/src.bin", str(dest))
    assert result.returncode == 0, result.stderr
    assert dest.read_bytes() == payload

import uuid


def test_cp_s3_to_local_writes_byte_identical_file(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = b"download-bytes-XYZ"
    s3_client.put_object(Bucket=bucket, Key="from-s3.bin", Body=payload)

    dst = tmp_path / "out.bin"

    result = cli("s3", "cp", f"s3://{bucket}/from-s3.bin", str(dst))
    assert result.returncode == 0, result.stderr
    assert dst.read_bytes() == payload

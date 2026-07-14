import uuid


def test_cp_local_to_s3_trailing_slash_infers_key(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "data.bin"
    payload = b"infer-key"
    src.write_bytes(payload)

    result = cli("s3", "cp", str(src), f"s3://{bucket}/")
    assert result.returncode == 0, result.stderr

    assert s3_client.get_object(Bucket=bucket, Key="data.bin")["Body"].read() == payload

import uuid


def test_zhard1_cp_binary_all_bytes_byte_perfect(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "all_bytes.bin"
    data = bytes(range(256)) * 16
    src.write_bytes(data)
    r = cli("s3", "cp", str(src), f"s3://{bucket}/k")
    assert r.returncode == 0, r.stderr
    body = s3_client.get_object(Bucket=bucket, Key="k")["Body"].read()
    assert body == data, f"content mismatch: {len(body)} got vs {len(data)} expected"

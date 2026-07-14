import uuid


def test_cp_s3_to_s3_cross_bucket(cli, s3_client):
    b1 = f"test-{uuid.uuid4().hex[:12]}"
    b2 = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=b1)
    s3_client.create_bucket(Bucket=b2)
    payload = b"cross-bucket-cp-bytes"
    s3_client.put_object(Bucket=b1, Key="k.bin", Body=payload)

    result = cli("s3", "cp", f"s3://{b1}/k.bin", f"s3://{b2}/k.bin")
    assert result.returncode == 0, result.stderr

    body = s3_client.get_object(Bucket=b2, Key="k.bin")["Body"].read()
    assert body == payload
    assert s3_client.get_object(Bucket=b1, Key="k.bin")["Body"].read() == payload

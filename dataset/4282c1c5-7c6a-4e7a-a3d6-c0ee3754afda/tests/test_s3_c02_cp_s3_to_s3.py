import uuid


def test_cp_s3_to_s3_creates_independent_copy(cli, s3_client):
    src_b = f"src-{uuid.uuid4().hex[:10]}"
    dst_b = f"dst-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=src_b)
    s3_client.create_bucket(Bucket=dst_b)
    payload = b"cross-bucket-copy"
    s3_client.put_object(Bucket=src_b, Key="obj.bin", Body=payload)

    result = cli("s3", "cp", f"s3://{src_b}/obj.bin", f"s3://{dst_b}/obj.bin")
    assert result.returncode == 0, result.stderr

    assert s3_client.get_object(Bucket=src_b, Key="obj.bin")["Body"].read() == payload
    assert s3_client.get_object(Bucket=dst_b, Key="obj.bin")["Body"].read() == payload

import uuid


def test_cp_s3_to_s3_creates_independent_copy(cli, s3_client):
    src_bucket = f"src-{uuid.uuid4().hex[:10]}"
    dst_bucket = f"dst-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=src_bucket)
    s3_client.create_bucket(Bucket=dst_bucket)
    payload = b"s3-to-s3-bytes"
    s3_client.put_object(Bucket=src_bucket, Key="origin.bin", Body=payload)

    result = cli(
        "s3", "cp",
        f"s3://{src_bucket}/origin.bin",
        f"s3://{dst_bucket}/copy.bin",
    )
    assert result.returncode == 0, result.stderr

    assert s3_client.get_object(Bucket=src_bucket, Key="origin.bin")["Body"].read() == payload
    assert s3_client.get_object(Bucket=dst_bucket, Key="copy.bin")["Body"].read() == payload

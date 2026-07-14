import hashlib
import uuid


def test_mv_dst_bytes_identical_to_src(cli, s3_client):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = b"\x00\x01\x02\x03move-bytes-PAYLOAD\xff\xfe\xfd"
    s3_client.put_object(Bucket=bucket, Key="src.bin", Body=payload)
    src_hash = hashlib.sha256(payload).hexdigest()

    result = cli("s3", "mv", f"s3://{bucket}/src.bin", f"s3://{bucket}/dst.bin")
    assert result.returncode == 0, result.stderr

    body = s3_client.get_object(Bucket=bucket, Key="dst.bin")["Body"].read()
    assert hashlib.sha256(body).hexdigest() == src_hash
    assert body == payload

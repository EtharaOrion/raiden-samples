import hashlib
import uuid


def test_e11_default_copy_preserves_sha256(cli, s3_client, tmp_path):
    """Default cp s3->s3 of 14 MiB object: dest sha256 matches src."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = (b"abcdefghij" * ((14 * 1024 * 1024 // 10) + 1))[: 14 * 1024 * 1024]
    src = tmp_path / "big.bin"
    src.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/src")
    assert r1.returncode == 0, r1.stderr
    r2 = cli("s3", "cp", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r2.returncode == 0, r2.stderr
    dst_body = s3_client.get_object(Bucket=bucket, Key="dst")["Body"].read()
    assert hashlib.sha256(dst_body).hexdigest() == expected

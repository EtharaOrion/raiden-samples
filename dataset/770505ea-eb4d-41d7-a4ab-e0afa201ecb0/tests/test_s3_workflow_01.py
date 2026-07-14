from _s3_http import S3HTTPError as ClientError


import pytest


def test_workflow_cp_roundtrip_identity(cli, s3_client, tmp_path):
    bucket = "test-roundtrip-bucket-abc789"
    
    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0
    
    src = tmp_path / "source.bin"
    payload = bytes(range(256)) * 8
    src.write_bytes(payload)
    
    result = cli("s3", "cp", str(src), f"s3://{bucket}/blob.bin")
    assert result.returncode == 0
    
    obj = s3_client.get_object(Bucket=bucket, Key="blob.bin")
    assert obj["Body"].read() == payload
    
    dst = tmp_path / "dest.bin"
    result = cli("s3", "cp", f"s3://{bucket}/blob.bin", str(dst))
    assert result.returncode == 0
    
    assert dst.read_bytes() == src.read_bytes()
    
    result = cli("s3", "mv", f"s3://{bucket}/blob.bin", f"s3://{bucket}/blob2.bin")
    assert result.returncode == 0
    
    with pytest.raises(ClientError) as exc_info:
        s3_client.head_object(Bucket=bucket, Key="blob.bin")
    assert exc_info.value.response["Error"]["Code"] in ("404", "NoSuchKey")
    
    moved = s3_client.get_object(Bucket=bucket, Key="blob2.bin")
    assert moved["Body"].read() == payload

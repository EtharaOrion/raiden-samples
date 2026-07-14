from _s3_http import S3HTTPError as ClientError


import pytest


def test_workflow_mb_cp_rm_lifecycle(cli, s3_client, tmp_path):
    bucket = "test-lifecycle-bucket-xyz123"
    
    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0
    
    buckets = [b["Name"] for b in s3_client.list_buckets()["Buckets"]]
    assert bucket in buckets
    
    local_file = tmp_path / "data.txt"
    payload = b"hello world\nthis is test data\n"
    local_file.write_bytes(payload)
    
    result = cli("s3", "cp", str(local_file), f"s3://{bucket}/data.txt")
    assert result.returncode == 0
    
    obj = s3_client.get_object(Bucket=bucket, Key="data.txt")
    assert obj["Body"].read() == payload
    
    result = cli("s3", "ls", f"s3://{bucket}/")
    assert result.returncode == 0
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "data.txt" in keys
    
    result = cli("s3", "rm", f"s3://{bucket}/data.txt")
    assert result.returncode == 0
    
    with pytest.raises(ClientError) as exc_info:
        s3_client.head_object(Bucket=bucket, Key="data.txt")
    assert exc_info.value.response["Error"]["Code"] in ("404", "NoSuchKey")
    
    contents = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    assert contents == []

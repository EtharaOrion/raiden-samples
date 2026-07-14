


def test_workflow_mv_self_negative_leaves_object(cli, s3_client, tmp_path):
    bucket = "test-negmv-bucket-qwe456"
    
    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0
    
    local_file = tmp_path / "file.txt"
    payload = b"important content that must survive"
    local_file.write_bytes(payload)
    
    result = cli("s3", "cp", str(local_file), f"s3://{bucket}/keep.txt")
    assert result.returncode == 0
    
    obj = s3_client.get_object(Bucket=bucket, Key="keep.txt")
    assert obj["Body"].read() == payload
    
    result = cli("s3", "mv", f"s3://{bucket}/keep.txt", f"s3://{bucket}/keep.txt")
    assert result.returncode != 0
    
    obj = s3_client.get_object(Bucket=bucket, Key="keep.txt")
    assert obj["Body"].read() == payload
    
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "keep.txt" in keys

import uuid


def test_rm_recursive_flag_clears_subprefix_only(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    for k in ("logs/2024/a.log", "logs/2024/b.log", "logs/2025/c.log"):
        s3_client.put_object(Bucket=bucket, Key=k, Body=b"L")
    s3_client.put_object(Bucket=bucket, Key="keep.txt", Body=b"K")

    result = cli("s3", "rm", f"s3://{bucket}/logs/2024", "--recursive")
    assert result.returncode == 0, result.stderr

    remaining = {
        o["Key"]
        for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []
    }
    assert remaining == {"logs/2025/c.log", "keep.txt"}

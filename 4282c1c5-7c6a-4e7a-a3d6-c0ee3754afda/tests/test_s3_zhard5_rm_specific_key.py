import uuid


def test_zhard5_rm_removes_specified_key_only(cli, s3_client):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="k1", Body=b"one")
    s3_client.put_object(Bucket=bucket, Key="k2", Body=b"two")
    r = cli("s3", "rm", f"s3://{bucket}/k1")
    assert r.returncode == 0, r.stderr
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "k1" not in keys, f"k1 was not deleted; remaining keys: {keys}"
    assert "k2" in keys, f"k2 was incorrectly affected; remaining keys: {keys}"

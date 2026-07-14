

import uuid


def test_workflow_mv_self_negative_leaves_state(cli, s3_client, tmp_path):
    bucket = f"test-bucket-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "f.txt"
    payload = b"persistent-bytes-xyz"
    src.write_bytes(payload)

    result = cli("s3", "cp", str(src), f"s3://{bucket}/k.txt")
    assert result.returncode == 0
    assert s3_client.get_object(Bucket=bucket, Key="k.txt")["Body"].read() == payload

    result = cli("s3", "mv", f"s3://{bucket}/k.txt", f"s3://{bucket}/k.txt")
    assert result.returncode != 0

    body = s3_client.get_object(Bucket=bucket, Key="k.txt")["Body"].read()
    assert body == payload

    result = cli("s3", "rm", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0

    contents = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    assert len(contents) == 0

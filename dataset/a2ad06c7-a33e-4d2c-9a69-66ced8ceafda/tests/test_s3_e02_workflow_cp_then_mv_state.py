import uuid

from _s3_http import S3HTTPError as ClientError


def test_workflow_cp_upload_then_mv_to_new_key(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "f.bin"
    payload = b"cp-then-mv-payload"
    src.write_bytes(payload)

    r = cli("s3", "cp", str(src), f"s3://{bucket}/orig.bin")
    assert r.returncode == 0, r.stderr
    assert s3_client.get_object(Bucket=bucket, Key="orig.bin")["Body"].read() == payload

    r = cli("s3", "mv", f"s3://{bucket}/orig.bin", f"s3://{bucket}/renamed.bin")
    assert r.returncode == 0, r.stderr
    assert s3_client.get_object(Bucket=bucket, Key="renamed.bin")["Body"].read() == payload
    try:
        s3_client.head_object(Bucket=bucket, Key="orig.bin")
        raise AssertionError("source should be absent")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")

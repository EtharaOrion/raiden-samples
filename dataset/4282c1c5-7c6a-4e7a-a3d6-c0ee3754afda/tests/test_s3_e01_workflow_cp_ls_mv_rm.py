import uuid

from _s3_http import S3HTTPError as ClientError


def test_workflow_cp_ls_mv_rm_lifecycle(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "f.bin"
    payload = b"workflow-payload"
    src.write_bytes(payload)

    r_cp = cli("s3", "cp", str(src), f"s3://{bucket}/f.bin")
    assert r_cp.returncode == 0, r_cp.stderr
    assert s3_client.get_object(Bucket=bucket, Key="f.bin")["Body"].read() == payload

    r_ls = cli("s3", "ls", f"s3://{bucket}/")
    assert r_ls.returncode == 0, r_ls.stderr
    assert "f.bin" in r_ls.stdout

    r_mv = cli("s3", "mv", f"s3://{bucket}/f.bin", f"s3://{bucket}/moved.bin")
    assert r_mv.returncode == 0, r_mv.stderr
    assert s3_client.get_object(Bucket=bucket, Key="moved.bin")["Body"].read() == payload
    try:
        s3_client.head_object(Bucket=bucket, Key="f.bin")
        raise AssertionError("source should be gone after mv")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")

    r_rm = cli("s3", "rm", f"s3://{bucket}/moved.bin")
    assert r_rm.returncode == 0, r_rm.stderr
    try:
        s3_client.head_object(Bucket=bucket, Key="moved.bin")
        raise AssertionError("object should be gone after rm")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")

from _s3_http import S3HTTPError as ClientError


def test_workflow_sync_roundtrip_mv_identity(cli, s3_client, tmp_path):
    bucket = "test-roundtrip-bucket-xyz123"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    src = tmp_path / "src"
    src.mkdir()
    payload1 = b"binary\x00\x01\x02data-one"
    payload2 = b"second\xfffile\x00content"
    (src / "one.bin").write_bytes(payload1)
    (src / "two.bin").write_bytes(payload2)

    r = cli("s3", "sync", str(src), f"s3://{bucket}")
    assert r.returncode == 0

    assert s3_client.get_object(Bucket=bucket, Key="one.bin")["Body"].read() == payload1
    assert s3_client.get_object(Bucket=bucket, Key="two.bin")["Body"].read() == payload2

    r = cli("s3", "mv", f"s3://{bucket}/one.bin", f"s3://{bucket}/renamed.bin")
    assert r.returncode == 0

    try:
        s3_client.head_object(Bucket=bucket, Key="one.bin")
        raise AssertionError("source should be gone after mv")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
    assert s3_client.get_object(Bucket=bucket, Key="renamed.bin")["Body"].read() == payload1

    dst = tmp_path / "dst"
    dst.mkdir()
    r = cli("s3", "sync", f"s3://{bucket}", str(dst))
    assert r.returncode == 0

    assert (dst / "renamed.bin").read_bytes() == payload1
    assert (dst / "two.bin").read_bytes() == payload2

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0

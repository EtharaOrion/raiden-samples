import uuid


def test_mv04_s3_to_s3_mv_byte_identical(cli, s3_client, tmp_path):
    """s3->s3 mv of arbitrary bytes: src gone, dst exact match."""
    src_bucket = f"test-{uuid.uuid4().hex[:12]}"
    dst_bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=src_bucket)
    s3_client.create_bucket(Bucket=dst_bucket)
    payload = bytes(range(256))
    s3_client.put_object(Bucket=src_bucket, Key="k", Body=payload)
    r = cli("s3", "mv", f"s3://{src_bucket}/k", f"s3://{dst_bucket}/k")
    assert r.returncode == 0, r.stderr
    from _s3_http import S3HTTPError as ClientError
    try:
        s3_client.head_object(Bucket=src_bucket, Key="k")
        raise AssertionError("source should be absent after mv")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey"), e
    body = s3_client.get_object(Bucket=dst_bucket, Key="k")["Body"].read()
    assert body == payload, "destination bytes differ from source"

import uuid

from _s3_http import S3HTTPError as ClientError


def test_mv_head_object_src_404_dst_200(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = b"head-check-payload"
    s3_client.put_object(Bucket=bucket, Key="src.bin", Body=payload)

    result = cli("s3", "mv", f"s3://{bucket}/src.bin", f"s3://{bucket}/dst.bin")
    assert result.returncode == 0, result.stderr

    dst_head = s3_client.head_object(Bucket=bucket, Key="dst.bin")
    assert dst_head["ContentLength"] == len(payload)
    assert s3_client.get_object(Bucket=bucket, Key="dst.bin")["Body"].read() == payload

    try:
        s3_client.head_object(Bucket=bucket, Key="src.bin")
        raise AssertionError("src head should return 404 after mv")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")

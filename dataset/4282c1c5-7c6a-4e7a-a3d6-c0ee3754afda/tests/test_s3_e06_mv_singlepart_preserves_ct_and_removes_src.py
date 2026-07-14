import uuid

from _s3_http import S3HTTPError as ClientError

def test_e06_mv_singlepart_preserves_ct_and_removes_src(cli, s3_client, tmp_path):
    """mv s3->s3 of singlepart object preserves ContentType and removes source."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(
        Bucket=bucket, Key="src", Body=b"k" * 1024, ContentType="text/csv"
    )
    r = cli("s3", "mv", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="dst")
    assert head["ContentType"] == "text/csv", head.get("ContentType")
    try:
        s3_client.head_object(Bucket=bucket, Key="src")
        raise AssertionError("source should be gone")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey"), e

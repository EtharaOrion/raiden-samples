import uuid


def test_mv02_s3_to_s3_mv_preserves_content_type(cli, s3_client, tmp_path):
    """s3->s3 mv WITHOUT --metadata-directive preserves source ContentType."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(
        Bucket=bucket, Key="src", Body=b"hi", ContentType="text/csv"
    )
    r = cli("s3", "mv", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="dst")
    assert head["ContentType"] == "text/csv", head.get("ContentType")

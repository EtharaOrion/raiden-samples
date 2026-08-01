import uuid


def test_mv05_default_mv_preserves_user_metadata(cli, s3_client, tmp_path):
    """Default mv s3->s3 preserves source user metadata on destination."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(
        Bucket=bucket, Key="src", Body=b"hi", Metadata={"author": "bob"}
    )
    r = cli("s3", "mv", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="dst")
    md = head.get("Metadata", {})
    assert md.get("author") == "bob", f"author metadata not preserved: {md!r}"

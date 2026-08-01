import uuid


def test_cp20_default_copy_preserves_content_language(cli, s3_client, tmp_path):
    """Default cp s3->s3 (no --metadata-directive) must preserve source metadata."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="src", Body=b"payload", ContentLanguage="en-US")
    r = cli("s3", "cp", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="dst")
    assert head.get("ContentLanguage") == "en-US"

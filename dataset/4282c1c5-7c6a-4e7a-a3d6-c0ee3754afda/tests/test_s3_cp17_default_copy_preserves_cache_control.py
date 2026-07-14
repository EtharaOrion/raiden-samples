import uuid


def test_cp17_default_copy_preserves_cache_control(cli, s3_client, tmp_path):
    """Default cp s3->s3 (no --metadata-directive) must preserve source metadata."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="src", Body=b"payload", CacheControl="max-age=3600")
    r = cli("s3", "cp", f"s3://{bucket}/src", f"s3://{bucket}/dst")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="dst")
    assert head.get("CacheControl") == "max-age=3600", f"got {head.get(chr(34) + chr(67) + chr(97) + chr(99) + chr(104) + chr(101) + chr(67) + chr(111) + chr(110) + chr(116) + chr(114) + chr(111) + chr(108) + chr(34))!r}"

import uuid


def test_cp64_multipart_plus_content_type_json(cli, s3_client, tmp_path):
    """10 MiB upload + --content-type: ETag multipart AND ContentType applied."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "doc.json"
    src.write_bytes(b"J" * (10 * 1024 * 1024))
    r = cli(
        "s3", "cp", str(src), f"s3://{bucket}/doc.json",
        "--content-type", "application/json",
    )
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="doc.json")
    etag = head["ETag"].strip('"')
    assert "-" in etag, f"expected multipart ETag, got {etag!r}"
    assert head["ContentType"] == "application/json", head.get("ContentType")

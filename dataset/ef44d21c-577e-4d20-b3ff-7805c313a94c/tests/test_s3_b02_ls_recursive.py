import uuid


def test_ls_recursive_walks_subprefixes(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="root.txt", Body=b"r")
    s3_client.put_object(Bucket=bucket, Key="dir1/inner.txt", Body=b"i")
    s3_client.put_object(Bucket=bucket, Key="dir1/sub/deep.txt", Body=b"d")

    result = cli("s3", "ls", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0, result.stderr

    assert "root.txt" in result.stdout
    assert "dir1/inner.txt" in result.stdout
    assert "dir1/sub/deep.txt" in result.stdout
    assert " PRE " not in result.stdout

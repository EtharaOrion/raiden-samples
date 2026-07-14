import uuid


def test_ls_page_size_returns_all_objects(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    for i in range(7):
        s3_client.put_object(Bucket=bucket, Key=f"k{i:02d}.txt", Body=str(i).encode())

    result = cli("s3", "ls", f"s3://{bucket}/", "--page-size", "2")
    assert result.returncode == 0, result.stderr

    for i in range(7):
        assert f"k{i:02d}.txt" in result.stdout

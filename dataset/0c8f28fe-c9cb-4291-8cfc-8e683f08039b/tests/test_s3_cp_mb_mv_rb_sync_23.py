

def test_sync_creates_non_existent_local_directory(cli, s3_client, tmp_path):
    bucket = 'bucket'
    key = 'foo.txt'
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key=key, Body=b'foo')

    non_existent_dir = tmp_path / 'fakedir'
    assert not non_existent_dir.exists()

    result = cli('s3', 'sync', f's3://{bucket}/', str(non_existent_dir))

    assert result.returncode == 0, f"stderr: {result.stderr}"
    downloaded = non_existent_dir / key
    assert downloaded.exists(), f"Expected {downloaded} to exist after sync"
    assert downloaded.read_bytes() == b'foo'

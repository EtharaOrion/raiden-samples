

def test_sync_to_non_existant_directory(cli, s3_client, tmp_path):
    bucket = 'bucket'
    key = 'foo.txt'
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key=key, Body=b'foo')

    non_existant_directory = tmp_path / 'fakedir'
    assert not non_existant_directory.exists()

    result = cli('s3', 'sync', f's3://{bucket}/', str(non_existant_directory))

    assert result.returncode == 0, f"stderr: {result.stderr}"
    downloaded = non_existant_directory / key
    assert downloaded.exists(), f"Expected {downloaded} to exist after sync"
    assert downloaded.read_bytes() == b'foo'

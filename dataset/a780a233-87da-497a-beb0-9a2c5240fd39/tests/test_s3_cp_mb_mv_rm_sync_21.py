

def test_sync_to_non_existent_directory(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='foo.txt', Body=b'foo')

    non_existent_directory = tmp_path / 'fakedir'

    result = cli('s3', 'sync', 's3://bucket/', str(non_existent_directory))

    assert result.returncode == 0, f"stderr: {result.stderr}"
    downloaded = non_existent_directory / 'foo.txt'
    assert downloaded.exists(), f"Expected file {downloaded} not created"
    assert downloaded.read_bytes() == b'foo'

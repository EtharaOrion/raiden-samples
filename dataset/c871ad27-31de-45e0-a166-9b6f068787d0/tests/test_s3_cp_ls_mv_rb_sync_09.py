

def test_s3_ls_nonexistent_prefix_returns_error(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    result = cli('s3', 'ls', 's3://bucket/foo')
    assert result.returncode == 1

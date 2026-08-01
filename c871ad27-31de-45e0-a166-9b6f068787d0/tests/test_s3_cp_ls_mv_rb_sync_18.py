

def test_rb_force_nonexistent_bucket_fails(cli, s3_client):
    result = cli('s3', 'rb', 's3://nonexistent-bucket-xyz', '--force')
    assert result.returncode != 0

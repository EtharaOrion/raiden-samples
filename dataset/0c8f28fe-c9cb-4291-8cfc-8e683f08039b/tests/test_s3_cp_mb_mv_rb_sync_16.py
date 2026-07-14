

def test_rb_force_empty_bucket(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')

    result = cli('s3', 'rb', 's3://bucket', '--force')

    assert result.returncode == 0
    buckets = [b['Name'] for b in s3_client.list_buckets().get('Buckets', [])]
    assert 'bucket' not in buckets

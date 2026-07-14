

def test_rb_force_on_empty_bucket_removes_it(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')

    result = cli('s3', 'rb', 's3://bucket', '--force')

    assert result.returncode == 0
    existing = [b['Name'] for b in s3_client.list_buckets().get('Buckets', [])]
    assert 'bucket' not in existing



def test_rb_removes_empty_bucket(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    buckets_before = [b['Name'] for b in s3_client.list_buckets()['Buckets']]
    assert 'bucket' in buckets_before

    result = cli('s3', 'rb', 's3://bucket')
    assert result.returncode == 0, f"stderr: {result.stderr}"

    buckets_after = [b['Name'] for b in s3_client.list_buckets()['Buckets']]
    assert 'bucket' not in buckets_after

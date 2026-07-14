

def test_mb_creates_bucket(cli, s3_client):
    result = cli('s3', 'mb', 's3://bucket')
    assert result.returncode == 0
    buckets = [b['Name'] for b in s3_client.list_buckets()['Buckets']]
    assert 'bucket' in buckets

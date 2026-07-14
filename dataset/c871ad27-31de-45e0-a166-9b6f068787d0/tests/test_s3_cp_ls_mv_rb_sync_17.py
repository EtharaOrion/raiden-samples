

def test_rb_deletes_existing_bucket(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    assert any(b['Name'] == 'bucket' for b in s3_client.list_buckets()['Buckets'])

    result = cli('s3', 'rb', 's3://bucket')

    assert result.returncode == 0, result.stderr
    remaining = [b['Name'] for b in s3_client.list_buckets()['Buckets']]
    assert 'bucket' not in remaining



def test_rb_failed_nonexistent_bucket(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'rb', 's3://nonexistent-bucket-xyz-12345')

    assert result.returncode != 0, f"expected 1, got {result.returncode}; stderr={result.stderr!r}"

    names = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'nonexistent-bucket-xyz-12345' not in names
    assert 'decoy-bucket-do-not-touch' in names

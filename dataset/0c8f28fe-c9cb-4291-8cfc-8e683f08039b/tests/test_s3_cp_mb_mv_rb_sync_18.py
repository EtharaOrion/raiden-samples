

def test_rb_force_nonexistent_bucket_fails(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'rb', 's3://nonexistent-bucket-xyz', '--force')

    assert result.returncode != 0, f"expected non-zero, got {result.returncode}; stderr={result.stderr!r}"

    names = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'nonexistent-bucket-xyz' not in names
    assert 'decoy-bucket-do-not-touch' in names

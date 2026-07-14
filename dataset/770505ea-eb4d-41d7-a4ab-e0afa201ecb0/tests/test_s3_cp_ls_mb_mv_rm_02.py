

def test_mb_directory_bucket_incompatible(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'mb', 's3://bucket--usw2-az1--x-s3/')

    assert result.returncode != 0, f"expected non-zero, got {result.returncode}; stderr={result.stderr!r}"

    names = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'bucket--usw2-az1--x-s3' not in names
    assert 'decoy-bucket-do-not-touch' in names



def test_mb_invalid_path_provided_returns_error(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'mb', 'bucket')

    assert result.returncode in (2, 252, 255), f"expected usage error, got {result.returncode}; stderr={result.stderr!r}"

    names = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'bucket' not in names
    assert 'decoy-bucket-do-not-touch' in names

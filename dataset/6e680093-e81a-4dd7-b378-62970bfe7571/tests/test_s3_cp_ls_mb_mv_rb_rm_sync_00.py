

def test_mb_invalid_path_returns_error(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'mb', 'bucket')

    assert result.returncode != 0, f"expected 255, got {result.returncode}; stderr={result.stderr!r}"

    names = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'bucket' not in names
    assert 'decoy-bucket-do-not-touch' in names

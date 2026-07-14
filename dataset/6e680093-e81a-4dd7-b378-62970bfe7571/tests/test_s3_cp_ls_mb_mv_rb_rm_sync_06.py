

def test_s3_ls_errors_out_with_extra_arguments(cli, s3_client):
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')

    result = cli('s3', 'ls', '--extra-argument-foo')

    assert result.returncode != 0, f"expected exit 255, got {result.returncode}; stderr={result.stderr!r}"

    buckets = {b['Name'] for b in s3_client.list_buckets().get('Buckets', [])}
    assert 'decoy-bucket-do-not-touch' in buckets

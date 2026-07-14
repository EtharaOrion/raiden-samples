

def test_sync_recursive_option_rejected(cli, s3_client):
    s3_client.create_bucket(Bucket='mybucket')
    result = cli('s3', 'sync', '.', 's3://mybucket', '--recursive')
    assert result.returncode != 0
    assert 'recursive' in (result.stderr + result.stdout).lower()

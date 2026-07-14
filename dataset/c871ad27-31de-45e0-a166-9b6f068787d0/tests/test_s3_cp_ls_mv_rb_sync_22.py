import os


def test_sync_from_nonexistent_directory_errors(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')
    non_existent = os.path.join(str(tmp_path), 'fakedir')
    assert not os.path.exists(non_existent)

    result = cli('s3', 'sync', non_existent, 's3://bucket/')

    assert result.returncode != 0

    resp = s3_client.list_objects_v2(Bucket='bucket')
    assert resp.get('KeyCount', 0) == 0
    buckets = {b['Name'] for b in s3_client.list_buckets()['Buckets']}
    assert 'decoy-bucket-do-not-touch' in buckets

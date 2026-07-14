import pytest


def test_mb_adds_location_constraint_us_west_2(cli, s3_client):
    result = cli('s3', 'mb', 's3://bucket', '--region', 'us-east-1')
    assert result.returncode == 0

    buckets = [b['Name'] for b in s3_client.list_buckets().get('Buckets', [])]
    assert 'bucket' in buckets

    location = s3_client.get_bucket_location(Bucket='bucket')
    assert location['LocationConstraint'] is None

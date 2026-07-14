import pytest


def test_mb_creates_bucket_with_location_constraint(cli, s3_client):
    result = cli('s3', 'mb', 's3://bucket', '--region', 'us-east-1')
    assert result.returncode == 0

    buckets = [b['Name'] for b in s3_client.list_buckets().get('Buckets', [])]
    assert 'bucket' in buckets

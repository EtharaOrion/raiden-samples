import pytest
def test_mb_us_east_1_omits_location_constraint(cli, s3_client):
    bucket = 'stump-east1-33'
    r = cli('s3', 'mb', f's3://{bucket}', '--region', 'us-east-1')
    assert r.returncode == 0
    loc = s3_client.get_bucket_location(Bucket=bucket).get('LocationConstraint')
    assert loc is None, f'us-east-1 must omit constraint, got LocationConstraint={loc!r}'


def test_mb_us_west_2_sets_location_constraint(cli, s3_client):
    bucket = 'stump-west2-34'
    r = cli('s3', 'mb', f's3://{bucket}', '--region', 'us-east-1')
    assert r.returncode == 0
    loc = s3_client.get_bucket_location(Bucket=bucket).get('LocationConstraint')
    assert loc is None, f'expected LocationConstraint=None (matching-region), got {loc!r}'

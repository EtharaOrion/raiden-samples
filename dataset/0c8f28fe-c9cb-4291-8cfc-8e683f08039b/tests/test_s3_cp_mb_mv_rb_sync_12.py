from conftest import _stderr_names_error


def test_mv_same_source_and_implied_dest_fails(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='key', Body=b'data')

    result = cli('s3', 'mv', 's3://bucket/key', 's3://bucket/')

    assert result.returncode != 0
    assert _stderr_names_error((result.stderr or '')) or 'itself' in (result.stderr or '').lower()

    head = s3_client.head_object(Bucket='bucket', Key='key')
    assert head['ContentLength'] == 4

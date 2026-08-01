from conftest import _stderr_names_error


def test_mv_object_onto_itself_implied_name_fails(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='key', Body=b'data')

    result = cli('s3', 'mv', 's3://bucket/key', 's3://bucket/')

    assert result.returncode != 0
    assert _stderr_names_error(result.stderr) or 'itself' in result.stderr.lower()

    resp = s3_client.get_object(Bucket='bucket', Key='key')
    assert resp['Body'].read() == b'data'

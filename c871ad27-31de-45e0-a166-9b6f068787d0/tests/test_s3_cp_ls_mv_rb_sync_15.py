from conftest import _stderr_names_error


def test_rb_nonexistent_bucket_fails(cli, s3_client):
    result = cli('s3', 'rb', 's3://nonexistent-bucket-xyz-12345')
    assert result.returncode != 0
    assert _stderr_names_error(result.stderr)

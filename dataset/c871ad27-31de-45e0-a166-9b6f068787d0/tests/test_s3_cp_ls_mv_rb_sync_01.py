import pytest


def test_cp_upload_with_sse_kms_and_key_id(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    file_path = tmp_path / 'foo.txt'
    file_path.write_text('contents')

    result = cli(
        's3', 'cp', str(file_path), 's3://bucket/key.txt',
        '--sse', 'aws:kms', '--sse-kms-key-id', 'foo'
    )

    assert result.returncode == 0

    response = s3_client.get_object(Bucket='bucket', Key='key.txt')
    assert response['Body'].read() == b'contents'

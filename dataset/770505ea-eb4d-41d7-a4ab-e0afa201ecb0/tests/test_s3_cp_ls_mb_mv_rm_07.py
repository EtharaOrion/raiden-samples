
def test_cp_upload_single_file_to_s3(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    file_path = tmp_path / 'foo.txt'
    file_path.write_text('mycontent')

    result = cli('s3', 'cp', str(file_path), 's3://bucket/key.txt')

    assert result.returncode == 0, result.stderr
    response = s3_client.get_object(Bucket='bucket', Key='key.txt')
    assert response['Body'].read() == b'mycontent'

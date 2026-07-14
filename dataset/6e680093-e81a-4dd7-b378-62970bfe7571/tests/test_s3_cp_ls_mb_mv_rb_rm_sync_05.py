

def test_cp_upload_single_file_puts_object(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    src = tmp_path / 'foo.txt'
    src.write_text('mycontent')

    result = cli('s3', 'cp', str(src), 's3://bucket/key.txt')

    assert result.returncode == 0, result.stderr
    resp = s3_client.get_object(Bucket='bucket', Key='key.txt')
    assert resp['Body'].read() == b'mycontent'

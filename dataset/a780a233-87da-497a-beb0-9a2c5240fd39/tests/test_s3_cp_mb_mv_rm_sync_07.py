

def test_cp_upload_local_file_to_s3(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    f = tmp_path / 'foo.txt'
    f.write_text('mycontent')

    result = cli('s3', 'cp', str(f), 's3://bucket/key.txt')
    assert result.returncode == 0, result.stderr

    resp = s3_client.get_object(Bucket='bucket', Key='key.txt')
    assert resp['Body'].read() == b'mycontent'

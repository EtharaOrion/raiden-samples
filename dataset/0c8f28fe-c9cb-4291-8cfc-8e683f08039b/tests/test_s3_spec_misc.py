def test_no_python_traceback_in_stderr_on_runtime_error(cli):
    r = cli('s3', 'rb', 's3://does-not-exist-stump-bucket-38')
    assert r.returncode != 0
    assert 'Traceback' not in r.stderr, f'raw traceback leaked to stderr:\n{r.stderr}'

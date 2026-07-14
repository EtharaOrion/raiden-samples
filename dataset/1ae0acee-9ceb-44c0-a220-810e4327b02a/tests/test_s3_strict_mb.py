def test_mb_no_arg_exits_255(cli):
    r = cli('s3', 'mb')
    assert r.returncode != 0


def test_mb_bare_no_scheme_v2_exits_255(cli):
    r = cli('s3', 'mb', 'no-scheme-40a')
    assert r.returncode != 0


def test_mb_too_short_exits_255(cli):
    r = cli('s3', 'mb', 's3://ab')
    assert r.returncode != 0

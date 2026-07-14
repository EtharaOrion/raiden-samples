def test_mb_no_arg_exits_255(cli):
    r = cli('s3', 'mb')
    assert r.returncode in (2, 252, 255)


def test_mb_bare_no_scheme_exits_255(cli):
    r = cli('s3', 'mb', 'noscheme-40a')
    assert r.returncode in (2, 252, 255)


def test_mb_too_short_exits_255(cli):
    r = cli('s3', 'mb', 's3://ab')
    assert r.returncode != 0

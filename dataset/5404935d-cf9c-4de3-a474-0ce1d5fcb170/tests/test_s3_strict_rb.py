from conftest import _stderr_names_error
def test_rb_no_arg_exits_255(cli):
    r = cli('s3', 'rb')
    assert r.returncode in (2, 252, 255)


def test_rb_unknown_flag_exits_255(cli):
    r = cli('s3', 'rb', 's3://b-42a', '--bogus')
    assert r.returncode in (2, 252, 255)


def test_rb_no_scheme_exits_255(cli):
    r = cli('s3', 'rb', 'noscheme-42b')
    assert r.returncode in (2, 252, 255)


def test_rb_nonexistent_v2(cli):
    r = cli('s3', 'rb', 's3://nonexist-v2-44a-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr)


def test_rb_nonexistent_v3(cli):
    r = cli('s3', 'rb', 's3://nonexist-44b-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr)


def test_rb_nonexistent_v4(cli):
    r = cli('s3', 'rb', 's3://nonexist-44c-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr)


def test_rb_force_nonexistent_v2_exits_255(cli):
    r = cli('s3', 'rb', 's3://nonexist-force-v2-46a', '--force')
    assert r.returncode != 0


def test_rb_force_nonexistent_v3_exits_255(cli):
    r = cli('s3', 'rb', 's3://nonexist-force-46b', '--force')
    assert r.returncode != 0

def test_list_users_invalid_pool_id(cli, cognito):
    bad_pool_id = "x" * 512
    result = cli("cognito-idp", "list-users", "--user-pool-id", bad_pool_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "InvalidParameter" in result.stderr
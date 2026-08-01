def test_list_users_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "list-users",
        "--user-pool-id", pool_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "attribute-definitions" in result.stderr

    # Pool itself should still be intact and usable via a valid ListUsers call
    listed = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert isinstance(listed.get("Users", []), list)
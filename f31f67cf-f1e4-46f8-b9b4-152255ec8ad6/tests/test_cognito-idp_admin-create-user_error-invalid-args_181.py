def test_admin_create_user_missing_required_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-create-user-missing-pool-id"},
    )["UserPool"]
    pool_id = pool["Id"]
    username = "user-without-pool-id"

    before = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(user["Username"] != username for user in before.get("Users", []))

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--username",
        username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    after = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(user["Username"] != username for user in after.get("Users", []))
def test_admin_set_user_password_nonexistent_user(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-set-password-nonexistent-user-pool"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "admin-set-user-password",
        "--user-pool-id",
        pool_id,
        "--username",
        "missing-user",
        "--password",
        "ValidPassword123!",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr

    pool = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert pool["UserPool"]["Name"] == "admin-set-password-nonexistent-user-pool"

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(user["Username"] != "missing-user" for user in users["Users"])
def test_admin_create_user_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-create-user-invalid-args"},
    )["UserPool"]
    pool_id = pool["Id"]

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        pool_id,
        "--username",
        "invalid-flag-user",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})["Users"]
    assert all(user["Username"] != "invalid-flag-user" for user in users)
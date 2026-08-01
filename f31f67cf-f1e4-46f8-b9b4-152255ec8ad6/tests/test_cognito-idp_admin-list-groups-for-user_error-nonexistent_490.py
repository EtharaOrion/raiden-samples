def test_admin_list_groups_for_user_nonexistent_user(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-list-groups-nonexistent-user"},
    )["UserPool"]
    pool_id = pool["Id"]

    result = cli(
        "cognito-idp",
        "admin-list-groups-for-user",
        "--username",
        "missing-user",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})["Users"]
    assert users == []
def test_admin_remove_user_from_group_nonexistent_user(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "remove-nonexistent-user-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    group_name = "existing-group"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )

    result = cli(
        "cognito-idp",
        "admin-remove-user-from-group",
        "--user-pool-id",
        pool_id,
        "--username",
        "nonexistent-user",
        "--group-name",
        group_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )["Group"]
    assert group["GroupName"] == group_name

    members = cognito.rpc(
        "ListUsersInGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )["Users"]
    assert members == []
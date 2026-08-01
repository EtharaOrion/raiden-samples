def test_admin_add_user_to_group_nonexistent_user(cli, cognito, tmp_path):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"pool-{tmp_path.name}"},
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

    before = cognito.rpc(
        "ListUsersInGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )
    assert before["Users"] == []

    result = cli(
        "cognito-idp",
        "admin-add-user-to-group",
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
    assert group["UserPoolId"] == pool_id

    after = cognito.rpc(
        "ListUsersInGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )
    assert after["Users"] == []
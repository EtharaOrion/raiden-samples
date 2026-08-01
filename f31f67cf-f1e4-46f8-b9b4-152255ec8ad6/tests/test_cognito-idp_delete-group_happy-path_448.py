def test_delete_group_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-group-happy-path-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]

    target_group = "group-to-delete"
    retained_group = "group-to-retain"

    cognito.rpc(
        "CreateGroup",
        {"UserPoolId": user_pool_id, "GroupName": target_group},
    )
    cognito.rpc(
        "CreateGroup",
        {"UserPoolId": user_pool_id, "GroupName": retained_group},
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        target_group,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc(
        "ListGroups",
        {"UserPoolId": user_pool_id, "Limit": 60},
    )["Groups"]
    group_names = {group["GroupName"] for group in groups}

    assert target_group not in group_names
    assert retained_group in group_names
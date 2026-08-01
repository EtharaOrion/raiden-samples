def test_delete_group_removes_existing_group(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-group-edge-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]
    group_name = "edge.group+name@example"

    created_group = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": user_pool_id,
            "GroupName": group_name,
            "Description": "Group to be deleted",
        },
    )["Group"]
    assert created_group["GroupName"] == group_name
    assert created_group["UserPoolId"] == user_pool_id

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc(
        "ListGroups",
        {"UserPoolId": user_pool_id, "Limit": 60},
    )["Groups"]
    assert all(group["GroupName"] != group_name for group in groups)
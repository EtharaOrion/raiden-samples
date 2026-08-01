def test_delete_group_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "delete-group-happy-path-group"

    created_group = cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Group to be deleted",
        },
    )["Group"]
    assert created_group["GroupName"] == group_name
    assert created_group["UserPoolId"] == pool_id

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert all(group["GroupName"] != group_name for group in groups)
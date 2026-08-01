def test_delete_group_removes_only_target_group(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-group-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    target_group = "edge-delete-target"
    retained_group = "edge-delete-retained"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": target_group,
            "Description": "Group to delete",
        },
    )
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": retained_group,
            "Description": "Group that must remain",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        target_group,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc(
        "ListGroups",
        {"UserPoolId": pool_id, "Limit": 60},
    )["Groups"]
    group_names = {group["GroupName"] for group in groups}

    assert target_group not in group_names
    assert retained_group in group_names
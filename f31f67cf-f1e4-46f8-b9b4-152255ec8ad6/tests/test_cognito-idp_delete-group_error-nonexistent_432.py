def test_delete_group_nonexistent_returns_resource_not_found(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-group-nonexistent-test"},
    )["UserPool"]
    pool_id = pool["Id"]

    existing_group_name = "existing-group"
    missing_group_name = "missing-group"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": existing_group_name,
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        missing_group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    group_names = {group["GroupName"] for group in groups}
    assert existing_group_name in group_names
    assert missing_group_name not in group_names
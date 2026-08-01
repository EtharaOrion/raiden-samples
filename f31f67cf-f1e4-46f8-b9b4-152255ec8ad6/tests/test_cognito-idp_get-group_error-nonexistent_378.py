def test_get_group_nonexistent_group_returns_resource_not_found(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-error-pool"})
    pool_id = pool["UserPool"]["Id"]

    existing_group_name = "existing-group"
    missing_group_name = "nonexistent-group"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": existing_group_name,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
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
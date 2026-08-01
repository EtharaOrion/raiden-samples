def test_delete_group_existing_group_succeeds(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-edge-pool"})["UserPool"]
    pool_id = pool["Id"]

    created = cognito.rpc(
        "CreateGroup",
        {"UserPoolId": pool_id, "GroupName": "x"},
    )["Group"]
    cognito.rpc(
        "CreateGroup",
        {"UserPoolId": pool_id, "GroupName": "preserved-group"},
    )

    assert created["GroupName"] == "x"
    assert created["UserPoolId"] == pool_id

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        "x",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id, "Limit": 60})["Groups"]
    group_names = {group["GroupName"] for group in groups}
    assert "x" not in group_names
    assert "preserved-group" in group_names
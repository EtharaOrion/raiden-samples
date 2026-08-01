def test_create_group_edge_happy_path(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "create-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "edge.group-1"

    before = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert all(group["GroupName"] != group_name for group in before["Groups"])

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )
    assert result.returncode == 0

    created = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert created["GroupName"] == group_name
    assert created["UserPoolId"] == pool_id
def test_create_group_with_zero_precedence(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "create-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "zero-precedence-group"

    before = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert all(group["GroupName"] != group_name for group in before["Groups"])

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--precedence",
        "0",
    )
    assert result.returncode == 0

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Precedence"] == 0
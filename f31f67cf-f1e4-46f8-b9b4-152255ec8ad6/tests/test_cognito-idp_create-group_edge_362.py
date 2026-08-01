def test_create_group_with_required_parameters(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "create-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        "x",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0, result.stderr

    group = cognito.rpc(
        "GetGroup",
        {
            "GroupName": "x",
            "UserPoolId": pool_id,
        },
    )["Group"]
    assert group["GroupName"] == "x"
    assert group["UserPoolId"] == pool_id
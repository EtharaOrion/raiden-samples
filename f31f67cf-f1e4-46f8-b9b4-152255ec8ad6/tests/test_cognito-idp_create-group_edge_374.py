def test_create_group_with_role_arn(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-group-role-arn-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        "role-arn-group",
        "--user-pool-id",
        pool_id,
        "--role-arn",
        "xxxxxxxxxxxxxxxxxxxx",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == "role-arn-group"
    assert output["Group"]["UserPoolId"] == pool_id

    group = cognito.rpc(
        "GetGroup",
        {
            "GroupName": "role-arn-group",
            "UserPoolId": pool_id,
        },
    )["Group"]
    assert group["GroupName"] == "role-arn-group"
    assert group["UserPoolId"] == pool_id
    assert group["RoleArn"] == "xxxxxxxxxxxxxxxxxxxx"
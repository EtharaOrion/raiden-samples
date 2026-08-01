def test_update_group_sets_minimum_length_role_arn(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-role-arn-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "update-group-role-arn-group"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "original description",
        },
    )

    role_arn = "xxxxxxxxxxxxxxxxxxxx"
    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--role-arn",
        role_arn,
    )

    assert result.returncode == 0

    group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
        },
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["RoleArn"] == role_arn
    assert group["Description"] == "original description"
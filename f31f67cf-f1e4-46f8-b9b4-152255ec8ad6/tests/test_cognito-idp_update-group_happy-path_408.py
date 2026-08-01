def test_update_group_existing_group_succeeds(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "update-group-happy-path"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "existing group",
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
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
    assert group["Description"] == "existing group"
    assert group["Precedence"] == 7
def test_update_group_accepts_maximum_length_group_name(cli, cognito):
    group_name = "x" * 128

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "existing description",
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
    assert group["Description"] == "existing description"
    assert group["Precedence"] == 7
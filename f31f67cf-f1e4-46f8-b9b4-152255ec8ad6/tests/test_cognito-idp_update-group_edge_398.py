def test_update_group_with_only_required_parameters(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-required-parameters-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "x",
            "Description": "original description",
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        "x",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == "x"
    assert output["Group"]["UserPoolId"] == pool_id

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": "x"},
    )["Group"]
    assert group["GroupName"] == "x"
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "original description"
    assert group["Precedence"] == 7
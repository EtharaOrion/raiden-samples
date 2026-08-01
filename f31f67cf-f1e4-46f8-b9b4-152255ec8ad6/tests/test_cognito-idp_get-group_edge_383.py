def test_get_group_max_length_name_success(cli, cognito):
    import json

    group_name = "x" * 128

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "get-group-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "maximum-length group name",
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == pool_id
    assert output["Group"]["Description"] == "maximum-length group name"
    assert output["Group"]["Precedence"] == 7

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == "maximum-length group name"
    assert stored_group["Precedence"] == 7
def test_get_group_with_max_length_group_name(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "g" * 128

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "edge-case group",
            "Precedence": 0,
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
    assert output["Group"]["Precedence"] == 0

    stored = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored["GroupName"] == group_name
    assert stored["UserPoolId"] == pool_id
    assert stored["Description"] == "edge-case group"
    assert stored["Precedence"] == 0
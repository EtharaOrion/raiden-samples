def test_update_group_happy_path(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-test-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "original description",
            "Precedence": 7,
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--group-name",
        "existing-group",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == "existing-group"
    assert output["Group"]["UserPoolId"] == pool_id

    stored_group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
        },
    )["Group"]
    assert stored_group["GroupName"] == "existing-group"
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == "original description"
    assert stored_group["Precedence"] == 7
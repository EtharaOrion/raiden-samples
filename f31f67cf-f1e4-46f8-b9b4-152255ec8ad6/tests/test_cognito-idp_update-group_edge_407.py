def test_update_group_with_only_required_arguments_preserves_properties(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "update-group-edge"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "description to preserve",
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
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == pool_id

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "description to preserve"
    assert group["Precedence"] == 7
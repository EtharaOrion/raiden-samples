def test_update_group_with_required_fields_succeeds(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool_name = f"update-group-pool-{suffix}"
    group_name = f"update-group-{suffix}"
    description = "existing group description"
    precedence = 7

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": description,
            "Precedence": precedence,
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

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == description
    assert stored_group["Precedence"] == precedence
def test_create_group_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "invalid-create-group-arguments-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "must-not-be-created"

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert all(group["GroupName"] != group_name for group in groups)
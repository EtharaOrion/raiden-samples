def test_get_group_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "get-group-invalid-args-group"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "group must remain unchanged",
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
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

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "group must remain unchanged"
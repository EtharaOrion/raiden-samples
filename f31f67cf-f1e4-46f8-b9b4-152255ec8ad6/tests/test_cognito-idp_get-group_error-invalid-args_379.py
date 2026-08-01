def test_get_group_missing_required_group_name(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "group must remain unchanged",
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--group-name" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": "existing-group"},
    )["Group"]
    assert group["GroupName"] == "existing-group"
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "group must remain unchanged"
def test_update_group_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "update-group-invalid-args-pool"})
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
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": "existing-group"},
    )["Group"]
    assert group["GroupName"] == "existing-group"
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "original description"
    assert group["Precedence"] == 7
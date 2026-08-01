def test_update_group_missing_required_group_name(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-group-missing-name-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "original description",
        },
    )

    result = cli(
        "cognito-idp",
        "update-group",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--group-name" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
        },
    )["Group"]
    assert group["GroupName"] == "existing-group"
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "original description"
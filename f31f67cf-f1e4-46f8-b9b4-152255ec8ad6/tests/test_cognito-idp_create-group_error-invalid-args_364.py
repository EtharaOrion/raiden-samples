def test_create_group_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "missing-pool-id-test"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        "invalid-args-group",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert all(
        group["GroupName"] != "invalid-args-group"
        for group in groups.get("Groups", [])
    )
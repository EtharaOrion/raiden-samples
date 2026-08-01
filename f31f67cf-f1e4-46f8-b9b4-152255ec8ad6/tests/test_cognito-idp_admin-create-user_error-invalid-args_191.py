def test_admin_create_user_rejects_empty_user_pool_id(cli, cognito, tmp_path):
    pool_name = f"invalid-pool-id-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert before.get("Users", []) == []

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        "",
        "--username",
        "<string>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert after.get("Users", []) == []
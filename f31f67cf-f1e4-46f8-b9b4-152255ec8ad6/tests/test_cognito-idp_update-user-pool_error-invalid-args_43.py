def test_update_user_pool_rejects_empty_user_pool_id(cli, cognito, tmp_path):
    pool_name = f"invalid-update-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert before["Name"] == pool_name

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert after["Id"] == pool_id
    assert after["Name"] == pool_name
def test_list_user_pools_rejects_unknown_flag(cli, cognito, tmp_path):
    pool_name = "invalid-args-" + tmp_path.name.replace("_", "-")
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert before["UserPool"]["Name"] == pool_name

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "10",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert after["UserPool"]["Id"] == pool_id
    assert after["UserPool"]["Name"] == pool_name
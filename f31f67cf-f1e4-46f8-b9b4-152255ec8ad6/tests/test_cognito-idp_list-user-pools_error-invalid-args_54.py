def test_list_user_pools_requires_max_results(cli, cognito, tmp_path):
    pool_name = f"missing-max-results-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli("cognito-idp", "list-user-pools")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--max-results" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name
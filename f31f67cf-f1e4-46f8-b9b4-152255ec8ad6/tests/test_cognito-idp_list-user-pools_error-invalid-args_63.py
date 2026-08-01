def test_list_user_pools_rejects_unknown_attribute_definitions(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-sentinel"})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "10",
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "invalid-args-sentinel"
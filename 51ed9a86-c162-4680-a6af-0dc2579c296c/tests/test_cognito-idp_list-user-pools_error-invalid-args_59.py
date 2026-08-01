def test_list_user_pools_invalid_args(cli, cognito):
    result = cli(
        "cognito-idp", "list-user-pools",
        "--max-results", "10",
        "--attribute-definitions", "{not valid json",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "argument" in result.stderr

    # Sanity check the server is still functional after the bad invocation.
    listing = cognito.rpc("ListUserPools", {"MaxResults": 10})
    assert "UserPools" in listing
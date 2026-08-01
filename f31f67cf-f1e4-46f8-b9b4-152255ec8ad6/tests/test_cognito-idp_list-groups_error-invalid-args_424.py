def test_list_groups_rejects_unknown_attribute_definitions(cli, cognito):
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc("CreateUserPool", {"PoolName": f"invalid-args-{suffix}"})
    pool_id = pool["UserPool"]["Id"]
    group_name = f"group-{suffix}"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "must remain unchanged",
        },
    )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert {group["GroupName"] for group in groups} == {group_name}
    assert groups[0]["Description"] == "must remain unchanged"
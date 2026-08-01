from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_before_and_after_create(cli, ddb_client, tmp_path):
    r1 = cli("dynamodb", "list-tables")
    assert r1.returncode == 0
    before = set(ddb_client.list_tables()["TableNames"])
    assert "Wf67New" not in before
    ddb_client.create_table(
        TableName="Wf67New",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r2 = cli("dynamodb", "list-tables")
    assert r2.returncode == 0
    assert "Wf67New" in ddb_client.list_tables()["TableNames"]

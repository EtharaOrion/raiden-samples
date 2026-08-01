from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_tables_after_create(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf15Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf15Tbl" in ddb_client.list_tables()["TableNames"]

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_shows_only_created(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf54Unique",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf54Unique",
                 "--item", '{"pk":{"S":"z"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = ddb_client.list_tables()["TableNames"]
    assert "Wf54Unique" in names
    assert "Wf54NonExistent" not in names

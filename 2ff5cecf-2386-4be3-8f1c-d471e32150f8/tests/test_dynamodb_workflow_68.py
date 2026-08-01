from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_numeric_key_absent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf69Tbl",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf69Tbl", Item={"id": {"N": "1"}})
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf69Tbl",
        "--key", '{"id":{"N":"999"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf69Tbl", Key={"id": {"N": "999"}})
    assert "Item" not in resp

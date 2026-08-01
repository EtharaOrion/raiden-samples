from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_isolation(cli, ddb_client):
    for name in ["Wf17TableA", "Wf17TableB"]:
        ddb_client.create_table(
            TableName=name,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    result = cli("dynamodb", "put-item", "--table-name", "Wf17TableA",
                 "--item", '{"pk":{"S":"same"},"loc":{"S":"A"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf17TableB",
                 "--item", '{"pk":{"S":"same"},"loc":{"S":"B"}}')
    assert result.returncode == 0
    ra = ddb_client.get_item(TableName="Wf17TableA", Key={"pk": {"S": "same"}})
    rb = ddb_client.get_item(TableName="Wf17TableB", Key={"pk": {"S": "same"}})
    assert from_item(ra["Item"])["loc"] == "A"
    assert from_item(rb["Item"])["loc"] == "B"

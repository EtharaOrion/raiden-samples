from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_updates_last_wins(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf64Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf64Table",
                 "--item", '{"pk":{"S":"lw1"},"v":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf64Table",
                 "--key", '{"pk":{"S":"lw1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"S":"b"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf64Table",
                 "--key", '{"pk":{"S":"lw1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"S":"c"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf64Table", Key={"pk": {"S": "lw1"}})
    assert from_item(resp["Item"])["v"] == "c"

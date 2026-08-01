from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_missing_table_after_put(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf20Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf20Table",
                 "--item", '{"pk":{"S":"p1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf20TableGhost",
                 "--key", '{"pk":{"S":"p1"}}',
                 "--update-expression", "SET a = :a",
                 "--expression-attribute-values", '{":a":{"S":"z"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf20Table", Key={"pk": {"S": "p1"}})
    assert "Item" in resp

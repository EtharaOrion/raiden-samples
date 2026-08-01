from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_missing_table_update(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf53Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf53Table",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf53Missing",
                 "--key", '{"pk":{"S":"a"}}',
                 "--update-expression", "SET x = :x",
                 "--expression-attribute-values", '{":x":{"S":"y"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

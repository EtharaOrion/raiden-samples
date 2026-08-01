from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_updateitem_reserved_word_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf6Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf6Table",
                 "--item", '{"pk":{"S":"r1"},"Status":{"S":"old"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf6Table",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr

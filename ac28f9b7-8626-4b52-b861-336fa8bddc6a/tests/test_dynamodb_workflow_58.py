from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_string_to_number_type(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf59Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf59Table",
                 "--item", '{"pk":{"S":"t1"},"v":{"S":"text"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf59Table",
                 "--key", '{"pk":{"S":"t1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf59Table", Key={"pk": {"S": "t1"}})
    assert from_item(resp["Item"])["v"] == 42

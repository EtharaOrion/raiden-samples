from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_update_missing_key_no_effect_other(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf37Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf37Table",
                 "--item", '{"pk":{"S":"orig"},"v":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf37Table",
                 "--key", '{"pk":{"S":"other"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf37Table", Key={"pk": {"S": "orig"}})
    assert from_item(resp["Item"])["v"] == "keep"

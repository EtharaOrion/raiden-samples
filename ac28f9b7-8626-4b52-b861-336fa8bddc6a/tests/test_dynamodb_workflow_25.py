from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_put_update(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf26Table",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "N"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf26Table",
                 "--item", '{"pk":{"S":"c"},"sk":{"N":"1"},"v":{"S":"init"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf26Table",
                 "--key", '{"pk":{"S":"c"},"sk":{"N":"1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"S":"upd"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf26Table", Key={"pk": {"S": "c"}, "sk": {"N": "1"}})
    assert from_item(resp["Item"])["v"] == "upd"

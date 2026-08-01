from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_updateitem_readback(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf2Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf2Table",
                 "--item", '{"pk":{"S":"k1"},"status":{"S":"old"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf2Table",
                 "--key", '{"pk":{"S":"k1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf2Table", Key={"pk": {"S": "k1"}})
    assert from_item(resp["Item"])["status"] == "new"

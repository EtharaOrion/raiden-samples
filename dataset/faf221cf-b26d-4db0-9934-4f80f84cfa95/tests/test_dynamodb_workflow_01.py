from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_put_update_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfPutUpd1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfPutUpd1",
                 "--item", '{"pk":{"S":"k1"},"status":{"S":"old"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfPutUpd1",
                 "--key", '{"pk":{"S":"k1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfPutUpd1", Key={"pk": {"S": "k1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["status"] == "new"

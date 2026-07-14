from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_update_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfPutUpd",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfPutUpd",
                 "--item", '{"pk":{"S":"u1"},"n":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfPutUpd",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode == 0
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfPutUpd", Key={"pk": {"S": "u1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["status"] == "active"

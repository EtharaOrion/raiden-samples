from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_update_creates_attribute(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpdNew1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfUpdNew1",
                 "--item", '{"pk":{"S":"un1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdNew1",
                 "--key", '{"pk":{"S":"un1"}}',
                 "--update-expression", "SET #c = :c",
                 "--expression-attribute-names", '{"#c":"count"}',
                 "--expression-attribute-values", '{":c":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfUpdNew1", Key={"pk": {"S": "un1"}})
    assert "Item" in resp
    assert resp["Item"]["count"] == {"N": "42"}

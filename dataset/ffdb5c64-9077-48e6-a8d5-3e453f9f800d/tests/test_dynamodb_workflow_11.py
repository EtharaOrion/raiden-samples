from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_creates_via_getitem(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblUpdCreate",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    resp = ddb_client.get_item(TableName="WfTblUpdCreate", Key={"pk": {"S": "n1"}})
    assert "Item" not in resp
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpdCreate",
                 "--key", '{"pk":{"S":"n1"}}',
                 "--update-expression", "SET #c = :v",
                 "--expression-attribute-names", '{"#c":"count"}',
                 "--expression-attribute-values", '{":v":{"N":"7"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblUpdCreate", Key={"pk": {"S": "n1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["count"] == 7

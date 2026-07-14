from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_update_expression_no_change(cli, ddb_client):
    table = "UpdItemErrTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "a1"}, "status": {"S": "old"}},
    )

    result = cli(
        "dynamodb", "update-item",
        "--table-name", "NoSuchTable_xyz",
        "--key", '{"pk":{"S":"a1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"new"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "a1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["status"] == {"S": "old"}
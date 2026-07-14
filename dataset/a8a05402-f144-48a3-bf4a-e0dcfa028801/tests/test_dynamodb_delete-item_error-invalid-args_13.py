from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_check_failed(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Tbl1",
        Item={"pk": {"S": "abc"}, "status": {"S": "active"}},
    )
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "Tbl1",
        "--key", '{"pk":{"S":"abc"}}',
        "--condition-expression", "#s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"inactive"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["status"]["S"] == "active"
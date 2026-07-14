from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblDelCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "TblDelCond1",
                 "--item", '{"pk":{"S":"d1"},"v":{"S":"keep"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "TblDelCond1",
                 "--key", '{"pk":{"S":"d1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="TblDelCond1", Key={"pk": {"S": "d1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "keep"

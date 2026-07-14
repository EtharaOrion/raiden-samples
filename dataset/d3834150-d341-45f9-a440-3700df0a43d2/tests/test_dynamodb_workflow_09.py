from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_condition_fails_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "TblCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"original"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "TblCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="TblCond1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "original"

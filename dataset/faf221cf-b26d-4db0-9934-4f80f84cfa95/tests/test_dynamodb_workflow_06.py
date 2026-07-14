from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_put_condition_not_exists_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"N":"99"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfCond1", Key={"pk": {"S": "c1"}})
    assert resp["Item"]["v"] == {"N": "1"}

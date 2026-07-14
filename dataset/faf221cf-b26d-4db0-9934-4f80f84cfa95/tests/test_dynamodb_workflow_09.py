from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_delete_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDelCond1",
                 "--item", '{"pk":{"S":"dc1"},"v":{"N":"3"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelCond1",
                 "--key", '{"pk":{"S":"dc1"}}',
                 "--condition-expression", "v = :chk",
                 "--expression-attribute-values", '{":chk":{"N":"77"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDelCond1", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
    assert resp["Item"]["v"] == {"N": "3"}

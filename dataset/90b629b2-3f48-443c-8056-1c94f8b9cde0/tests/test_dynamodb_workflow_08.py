from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_fails_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf9Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf9Tbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"first"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf9Tbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"second"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf9Tbl", Key={"pk": {"S": "c1"}})
    assert resp["Item"]["v"] == {"S": "first"}

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fail(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfReserved",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfReserved",
                 "--item", '{"pk":{"S":"r1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfReserved",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfReserved", Key={"pk": {"S": "r1"}})
    from _ddb_http import from_item
    assert "Status" not in from_item(resp["Item"])

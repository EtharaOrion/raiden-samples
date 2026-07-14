from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_fails(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfReserved1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfReserved1",
                 "--item", '{"pk":{"S":"r1"},"Status":{"S":"initial"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfReserved1",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"changed"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfReserved1", Key={"pk": {"S": "r1"}})
    assert from_item(resp["Item"])["Status"] == "initial"

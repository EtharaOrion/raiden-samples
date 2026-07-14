from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_reserved_word_unescaped_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblReserved1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblReserved1", Item={"pk": {"S": "r1"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfTblReserved1",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblReserved1", Key={"pk": {"S": "r1"}})
    assert "Status" not in resp["Item"]

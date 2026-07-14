from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_word_validation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfReservedTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    result = cli("dynamodb", "put-item", "--table-name", "WfReservedTbl",
                 "--item", '{"pk":{"S":"r1"},"Status":{"S":"init"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "WfReservedTbl",
                 "--key", '{"pk":{"S":"r1"}}',
                 "--update-expression", "SET Status = :v",
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.get_item(TableName="WfReservedTbl", Key={"pk": {"S": "r1"}})
    assert from_item(resp["Item"])["Status"] == "init"

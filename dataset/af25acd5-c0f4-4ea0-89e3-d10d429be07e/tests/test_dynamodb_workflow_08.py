from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_not_exists_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="PutCondTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "put-item", "--table-name", "PutCondTbl",
                 "--item", '{"pk":{"S":"p1"},"v":{"S":"orig"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "PutCondTbl",
                 "--item", '{"pk":{"S":"p1"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="PutCondTbl", Key={"pk": {"S": "p1"}})
    assert from_item(resp["Item"]) == {"pk": "p1", "v": "orig"}

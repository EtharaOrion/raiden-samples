from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_conditional_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "DelCondTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "DelCondTbl",
                 "--item", '{"pk":{"S":"d1"},"status":{"S":"active"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "DelCondTbl",
                 "--key", '{"pk":{"S":"d1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="DelCondTbl", Key={"pk": {"S": "d1"}})
    assert "Item" in resp
    assert from_item(resp["Item"]) == {"pk": "d1", "status": "active"}

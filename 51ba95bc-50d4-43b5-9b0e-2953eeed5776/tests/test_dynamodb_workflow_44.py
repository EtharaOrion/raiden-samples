from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_attribute_exists_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_aexok1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_aexok1",
                 "--item", '{"pk":{"S":"ae1"},"v":{"S":"init"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_aexok1",
                 "--item", '{"pk":{"S":"ae1"},"v":{"S":"updated"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_aexok1", Key={"pk": {"S": "ae1"}})
    assert from_item(resp["Item"]) == {"pk": "ae1", "v": "updated"}

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_success_then_verify_no_dup(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_csvn1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_csvn1",
                 "--item", '{"pk":{"S":"cn1"},"v":{"N":"100"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_csvn1",
                 "--key", '{"pk":{"S":"cn1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_csvn1", Key={"pk": {"S": "cn1"}})
    assert from_item(resp["Item"]) == {"pk": "cn1", "v": 100}

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_on_second_key_independent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_condind1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_condind1",
                 "--item", '{"pk":{"S":"exists"},"v":{"S":"e"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_condind1",
                 "--item", '{"pk":{"S":"fresh"},"v":{"S":"f"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_condind1", Key={"pk": {"S": "fresh"}})
    assert from_item(resp["Item"]) == {"pk": "fresh", "v": "f"}

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_success_new_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_condok1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_condok1",
                 "--item", '{"pk":{"S":"newk"},"v":{"S":"fresh"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_condok1", Key={"pk": {"S": "newk"}})
    assert from_item(resp["Item"]) == {"pk": "newk", "v": "fresh"}

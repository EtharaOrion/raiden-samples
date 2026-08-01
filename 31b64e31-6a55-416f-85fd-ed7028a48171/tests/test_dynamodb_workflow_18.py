from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_success_new_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf19Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf19Tbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"first"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf19Tbl", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"]) == {"pk": "c1", "v": "first"}

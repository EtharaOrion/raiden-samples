from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_attr_exists_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf47Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf47Tbl",
                 "--item", '{"pk":{"S":"e"},"v":{"S":"first"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf47Tbl",
                 "--item", '{"pk":{"S":"e"},"v":{"S":"second"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf47Tbl", Key={"pk": {"S": "e"}})
    assert from_item(resp["Item"]) == {"pk": "e", "v": "second"}

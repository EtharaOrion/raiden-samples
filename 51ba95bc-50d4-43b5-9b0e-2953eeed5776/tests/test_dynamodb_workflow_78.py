from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_success_overwrites_number(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cson1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cson1",
                 "--item", '{"pk":{"S":"co1"},"count":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cson1",
                 "--item", '{"pk":{"S":"co1"},"count":{"N":"2"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cson1", Key={"pk": {"S": "co1"}})
    assert from_item(resp["Item"]) == {"pk": "co1", "count": 2}

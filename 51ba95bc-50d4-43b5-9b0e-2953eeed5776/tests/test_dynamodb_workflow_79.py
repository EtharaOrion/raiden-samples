from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_across_two_created_tables(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gact_a",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gact_b",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gact_a",
                 "--item", '{"pk":{"S":"only_a"},"v":{"S":"a"}}')
    assert result.returncode == 0
    ra = ddb_client.get_item(TableName="Tbl_gact_a", Key={"pk": {"S": "only_a"}})
    rb = ddb_client.get_item(TableName="Tbl_gact_b", Key={"pk": {"S": "only_a"}})
    assert from_item(ra["Item"]) == {"pk": "only_a", "v": "a"}
    assert "Item" not in rb

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_items_shared_prefix_keys(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_pref1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_pref1",
                 "--item", '{"pk":{"S":"user#1"},"v":{"S":"first"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_pref1",
                 "--item", '{"pk":{"S":"user#2"},"v":{"S":"second"}}')
    assert result.returncode == 0
    r1 = ddb_client.get_item(TableName="Tbl_pref1", Key={"pk": {"S": "user#1"}})
    r2 = ddb_client.get_item(TableName="Tbl_pref1", Key={"pk": {"S": "user#2"}})
    assert from_item(r1["Item"])["v"] == "first"
    assert from_item(r2["Item"])["v"] == "second"

from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_with_many_types(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_mt2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_mt2",
                 "--item",
                 '{"pk":{"S":"mt2"},"s":{"S":"str"},"n":{"N":"11"},"b":{"BOOL":true},"nul":{"NULL":true},"lst":{"L":[{"N":"1"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_mt2", Key={"pk": {"S": "mt2"}})
    assert from_item(resp["Item"]) == {
        "pk": "mt2", "s": "str", "n": 11, "b": True, "nul": None, "lst": [1]}

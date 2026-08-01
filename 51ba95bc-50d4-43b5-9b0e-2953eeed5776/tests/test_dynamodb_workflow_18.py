from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_string_set_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ss1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ss1",
                 "--item", '{"pk":{"S":"set1"},"colors":{"SS":["red","green","blue"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_ss1", Key={"pk": {"S": "set1"}})
    native = from_item(resp["Item"])
    assert native["pk"] == "set1"
    assert set(native["colors"]) == {"red", "green", "blue"}

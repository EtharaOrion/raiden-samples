from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_creates_then_puts_both(cli, ddb_client, tmp_path):
    for name in ("Wf54A", "Wf54B"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf54A",
                 "--item", '{"pk":{"S":"1"},"n":{"N":"10"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf54B",
                 "--item", '{"pk":{"S":"1"},"n":{"N":"20"}}')
    assert result.returncode == 0
    tables = set(ddb_client.list_tables()["TableNames"])
    assert {"Wf54A", "Wf54B"}.issubset(tables)
    assert ddb_client.get_item(TableName="Wf54A", Key={"pk": {"S": "1"}})["Item"]["n"]["N"] == "10"
    assert ddb_client.get_item(TableName="Wf54B", Key={"pk": {"S": "1"}})["Item"]["n"]["N"] == "20"

from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_table_data_separation(cli, ddb_client, tmp_path):
    for name in ("Wf43A", "Wf43B"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf43A",
                 "--item", '{"pk":{"S":"k"},"t":{"S":"A"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf43B",
                 "--item", '{"pk":{"S":"k"},"t":{"S":"B"}}')
    assert result.returncode == 0
    ra = ddb_client.get_item(TableName="Wf43A", Key={"pk": {"S": "k"}})
    rb = ddb_client.get_item(TableName="Wf43B", Key={"pk": {"S": "k"}})
    assert from_item(ra["Item"])["t"] == "A"
    assert from_item(rb["Item"])["t"] == "B"

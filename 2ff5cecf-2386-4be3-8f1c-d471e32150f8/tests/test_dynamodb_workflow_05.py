from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_missing_table_fails(cli, ddb_client, tmp_path):
    assert "Wf6Missing" not in ddb_client.list_tables()["TableNames"]
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf6Missing",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

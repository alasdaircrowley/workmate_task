import pytest
import sys
from main import main

@pytest.fixture
def sample_csv(tmp_path):
    csv_data = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8
redmi note 12,xiaomi,199,4.6
poco x5 pro,xiaomi,299,4.4"""
    file_path = tmp_path / "sample.csv"
    file_path.write_text(csv_data)
    return str(file_path)

@pytest.fixture
def capsys_print(capsys):
    def _print():
        captured = capsys.readouterr()
        return captured.out.strip()
    return _print

@pytest.fixture
def mock_argv(monkeypatch):
    def _mock_argv(args):
        monkeypatch.setattr(sys, 'argv', ['main.py'] + args)
    return _mock_argv

def test_no_args(capsys_print, mock_argv):
    mock_argv([])
    with pytest.raises(SystemExit):
        main()
    output = capsys_print()
    assert "file" in output.lower() or "файл" in output.lower()

def test_show_all(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" in output
    assert "redmi note 12" in output
    assert "poco x5 pro" in output

def test_numeric_filter_gt(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price", ">", "500"])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" in output
    assert "redmi note 12" not in output
    assert "poco x5 pro" not in output

def test_numeric_filter_lt(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price", "<", "300"])
    main()
    output = capsys_print()
    assert "redmi note 12" in output
    assert "poco x5 pro" in output
    assert "iphone 15 pro" not in output
    assert "galaxy s23 ultra" not in output

def test_numeric_filter_eq(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price", "==", "999"])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" not in output
    assert "redmi note 12" not in output
    assert "poco x5 pro" not in output

def test_string_filter_eq(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "brand", "==", "apple"])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" not in output
    assert "redmi note 12" not in output
    assert "poco x5 pro" not in output

def test_string_filter_neq(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "brand", "!=", "xiaomi"])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" in output
    assert "redmi note 12" not in output
    assert "poco x5 pro" not in output

def test_agg_avg(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "avg(price)"])
    main()
    output = capsys_print()
    assert "avg(price) = 674.00" in output

def test_agg_min(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "min(price)"])
    main()
    output = capsys_print()
    assert "min(price) = 199" in output

def test_agg_max(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "max(rating)"])
    main()
    output = capsys_print()
    assert "max(rating) = 4.9" in output

def test_invalid_filter_format(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price>"])
    main()
    output = capsys_print()
    assert "Некорректный формат фильтра" in output

def test_unknown_column_filter(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "color == red"])
    main()
    output = capsys_print()
    assert "Колонка 'color' не найдена" in output

def test_unknown_operator(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price ~ 500"])
    main()
    output = capsys_print()
    assert "Не найден поддерживаемый оператор" in output

def test_invalid_agg_format(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "avg price"])
    main()
    output = capsys_print()
    assert "Некорректный формат агрегации" in output

def test_unknown_column_agg(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "avg(size)"])
    main()
    output = capsys_print()
    assert "Колонка 'size' не найдена" in output

def test_non_numeric_agg(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", "avg(name)"])
    main()
    output = capsys_print()
    assert "не является числом" in output

def test_empty_file(tmp_path, capsys_print, mock_argv):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("name,brand,price,rating")
    mock_argv([str(file_path)])
    main()
    output = capsys_print()
    assert "Файл пуст" in output

def test_no_matching_rows(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price > 2000"])
    main()
    output = capsys_print()
    assert "Нет данных, соответствующих фильтру" in output

def test_filter_with_spaces(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "   price   >   500   "])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" in output

def test_agg_with_spaces(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--agg", " avg( price ) "])
    main()
    output = capsys_print()
    assert "avg(price) = 674.00" in output

def test_filter_without_spaces(capsys_print, sample_csv, mock_argv):
    mock_argv([sample_csv, "--filter", "price>500"])
    main()
    output = capsys_print()
    assert "iphone 15 pro" in output
    assert "galaxy s23 ultra" in output
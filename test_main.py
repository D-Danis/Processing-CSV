import pytest
import sys
import tempfile
import os
import csv
from io import StringIO
from contextlib import redirect_stdout
from contextlib import nullcontext as does_not_raise


import main 


@pytest.fixture
def sample_csv():
    csv_content = """name,brand,price,rating
                    iphone 15 pro,apple,999,4.9
                    galaxy s23 ultra,samsung,1199,4.8
                    redmi note 12,xiaomi,199,4.6
                    poco x5 pro,xiaomi,299,4.4"""
      
    with tempfile.NamedTemporaryFile(
                mode='w+', 
                delete=False, 
                suffix='.csv', 
                encoding='utf-8') as f:
        f.write(csv_content)
        filename = f.name
    yield filename
    os.remove(filename)


def run_script_with_args(args):
    sys_argv_backup = sys.argv
    sys.argv = ['main.py'] + args
    try:
        buf = StringIO()
        with redirect_stdout(buf):
            main.main()
        return buf.getvalue()
    finally:
        sys.argv = sys_argv_backup


def test_order_by_desc(sample_csv):
    output = run_script_with_args([sample_csv,
                                   '--where', 'rating > 4.5', 
                                   '--order-by', 'rating=desc'])
    assert 'iphone 15 pro' in output.splitlines()[3] 


@pytest.mark.parametrize(
    "query, answer, expectation", 
    [
        (['--where', 'rating > 4.5'], 'iphone 15 pro', does_not_raise()),
        (['--where', 'invalid'], 'iphone 15 pro', pytest.raises(ValueError)),
        (['--aggregate', 'rating=avg'], '4.67', does_not_raise()),
        (['--aggregate', 'invalid'], '4.67', pytest.raises(ValueError)),
        (['--where', 'brand = xiaomi',
          '--aggregate', 'rating=min'], '4.4', does_not_raise()),
        (['--median', 'rating'], '4', does_not_raise()),
        (['--where', 'rating < 4.7',
          '--order-by', 'rating=asc',
          '--aggregate', 'rating=max'], '4.6', does_not_raise()),
        (['--where', 'rating > 4.5', 
         '--order-by', 'invalid'], 'iphone 15 pro', pytest.raises(ValueError))
    ])
def test_does_not_raise(sample_csv, query, answer, expectation):
    with expectation:
        output = run_script_with_args([sample_csv, *query])
        assert answer in output 
    

@pytest.mark.parametrize(
    "query, col, op, val",
    [
        ('rating > 4.5', 'rating', '>', '4.5'),
        ('brand = apple', 'brand', '=', 'apple'),
        ('price < 1000', 'price', '<', '1000')
    ]
)
def test_parse_where_condition(query, col, op, val):
    x, y, z = main.parse_where_condition(query)
    assert col == x
    assert op == y
    assert val == z


@pytest.mark.parametrize(
    "query, col, op",
    [
        ('rating=avg', 'rating', 'avg'),
        ('rating=max', 'rating', 'max'),
        ('rating=min', 'rating', 'min')
    ]
)
def test_parse_aggregate(query, col, op):
    x, y = main.parse_aggregate(query)
    assert col == x
    assert op == y


@pytest.mark.parametrize(
    "query, col, op",
    [
        ('brand=desc', 'brand', 'desc'),
        ('brand=asc', 'brand', 'asc')
    ]
)
def test_parse_order_by(query, col, op):
    x, y = main.parse_order_by(query)
    assert col == x
    assert op == y

    
def test_command_orderby_sort(sample_csv):
    cmd=main.OrderByCommand()
    data = main.read_csv(sample_csv)
    sorted_result=cmd.execute(data,type('Args', (), {'order_by':'rating=desc'})())
    assert sorted_result[0]['name'].strip()=='iphone 15 pro'
    

@pytest.mark.parametrize(
    "command, query",
    [
        (main.WhereCommand, {'where':'rating > 4.7'}),
        (main.AggregateCommand, {'aggregate':'rating=avg'}),
        (main.MedianCommand, {'median':'price'})
    ]
)
def test_command_filter(sample_csv, command, query):
    cmd = command()
    data = main.read_csv(sample_csv)
    filtered=cmd.execute(data,type('Args', (), {**query})())
    assert len(filtered) == 2
    

def test_read_csv(tmp_path):
    file_path=tmp_path / "test.csv"
    with open(file_path,'w') as f:
        writer=csv.DictWriter(f,['a','b'])
        writer.writeheader()
        writer.writerow({'a':'1','b':'x'})
        writer.writerow({'a':'2','b':'y'})

    data=main.read_csv(str(file_path))
    assert isinstance(data,list)
    assert data[0]['a']=='1'


def test_main_flow(monkeypatch,tmp_path):
    csv_path=str(tmp_path / "data.csv")
    with open(csv_path,'w') as f:
        writer =csv.DictWriter(f,['name','age'])
        writer.writeheader()
        writer.writerow({'name':'Anna','age':'28'})
        writer.writerow({'name':'Ben','age':'35'})

    args=['main.py', csv_path,'--where','age > 30']
    monkeypatch.setattr('sys.argv', args)

    main.main()

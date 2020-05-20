from my_interface import trade, ORDER_TYPE, ACTION
import dwx
from dwx import POS_OPEN
import pytest


@pytest.fixture
def irrelevant_symbol():
    return "irrelevant_symbol"


@pytest.fixture
def irrelevant_lots():
    return 1


@pytest.mark.parametrize("order_type", list(ORDER_TYPE))
def test_ORDER_TYPE__str__conversion(order_type):
    assert int(str(order_type)) == order_type
    assert int("{}".format(order_type)) == order_type


@pytest.mark.parametrize("order_type", [ORDER_TYPE.BUY, ORDER_TYPE.SELL])
def test_market_orders(order_type, irrelevant_symbol, irrelevant_lots):
    order_dict = trade(order_type, symbol=irrelevant_symbol, lots=irrelevant_lots)
    assert isinstance(order_dict["_action"], int)
    assert order_dict["_action"] == ACTION.POS_OPEN
    assert isinstance(order_dict["_type"], int)
    assert order_dict["_type"] == order_type


@pytest.mark.parametrize("order_type", [ORDER_TYPE.BUY_LIMIT, ORDER_TYPE.SELL_LIMIT])
def test_limit_orders(order_type, irrelevant_symbol, irrelevant_lots):
    order_dict = trade(order_type, symbol=irrelevant_symbol, lots=irrelevant_lots)
    assert isinstance(order_dict["_action"], int)
    assert order_dict["_action"] == ACTION.ORD_OPEN


def test_trade_fails_on_non_ORDER_TYPE(irrelevant_symbol, irrelevant_lots):
    with pytest.raises(RuntimeError):
        trade(0, symbol=irrelevant_symbol, lots=irrelevant_lots)


@pytest.mark.parametrize(
    "order_type",
    [
        ot
        for ot in ORDER_TYPE
        if ot
        not in [
            ORDER_TYPE.BUY,
            ORDER_TYPE.SELL,
            ORDER_TYPE.BUY_LIMIT,
            ORDER_TYPE.SELL_LIMIT,
        ]
    ],
)
def test_trade_fails_with_non_implemented_ACTIONs(
    order_type, irrelevant_symbol, irrelevant_lots
):
    with pytest.raises(NotImplementedError):
        trade(order_type, symbol=irrelevant_symbol, lots=irrelevant_lots)


class DWX_ZeroMQ_Connector_STUB(dwx.DWX_ZeroMQ_Connector):
    """Like DWX_ZeroMQ_Connector, but without the massive __init__ function"""

    def __init__(self, _ClientID="dwx-zeromq"):
        self._ClientID = _ClientID

    def _format_command_to_send(
        self,
        _action=POS_OPEN,
        _type=0,
        _symbol="EURUSD",
        _price=0.0,
        _SL=50,
        _TP=50,
        _comment="Python-to-MT",
        _lots=0.01,
        _magic=123456,
        _ticket=0,
    ):
        """This method is the first part of _DWX_MTX_SEND_COMMAND_"""
        _msg = "{};{};{};{};{};{};{};{};{};{}".format(
            _action, _type, _symbol, _price, _SL, _TP, _comment, _lots, _magic, _ticket
        )
        return _msg


def test_comparison_with_DWX_default_order_dict():

    dwx_stub = DWX_ZeroMQ_Connector_STUB()
    default_order_dict = dwx_stub._generate_default_order_dict()
    our_order_dict = trade(
        ORDER_TYPE(default_order_dict["_type"]),
        symbol=default_order_dict["_symbol"],
        price=default_order_dict["_price"],
        sl=default_order_dict["_SL"],
        tp=default_order_dict["_TP"],
        comment=default_order_dict["_comment"],
        lots=default_order_dict["_lots"],
        magic=default_order_dict["_magic"],
        ticket=default_order_dict["_ticket"],
    )
    for key in default_order_dict.keys():
        assert default_order_dict[key] == our_order_dict[key]
    assert dwx_stub._format_command_to_send(
        **default_order_dict
    ) == dwx_stub._format_command_to_send(**our_order_dict)

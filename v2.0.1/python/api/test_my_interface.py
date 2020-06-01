# local
from . import my_interface
from .my_interface import command, ORDER_TYPE, ACTION
# 3rd party
import pytest  # type: ignore
# stdlib
from warnings import catch_warnings


class DWX_ZeroMQ_Connector_STUB(my_interface.DWX_Connector):
    """Like DWX_ZeroMQ_Connector, but without the side effects."""

    def _create_sockets_and_initialize_poller(self):
        pass

    def _start_poller(self):
        pass

    def _setup_ZMQ_monitoring(self):
        pass

def test_my_DWX_Connector_wrapper_has_BUY_method_and_SELL_method_etc(stub_instance):
    for action in ACTION:
        assert hasattr(stub_instance, action.name)
    for order_type in ORDER_TYPE:
        assert hasattr(stub_instance, action.name)


def test_command_rejectes_kwargs_that_are_not_required(
    irrelevant_ticket, irrelevant_lots, irrelevant_sl
):
    """If a keyword arg is not REQUIRED by the given ACTION or ORDER_TYPE passed to
    `command`, then `command` should raise a TypeError"""
    with pytest.raises(TypeError) as excinfo:
        command(
            ACTION.POS_CLOSE_PARTIAL,
            ticket=irrelevant_ticket,
            lots=irrelevant_lots,
            sl=irrelevant_sl,
        )
    assert str(excinfo.value).startswith(
        "Got unexpected keyword argument 'sl' for action"
    )
    assert "POS_CLOSE_PARTIAL" in str(excinfo.value)


def test_ticket_tracking(stub_instance, irrelevant_ticket):
    assert stub_instance.ticket is None
    stub_instance._set_response_(dict(_ticket=irrelevant_ticket))
    assert stub_instance.ticket == irrelevant_ticket


def test_my_DWX_Connector_wrapper_has_send_command_method(stub_instance):
    assert hasattr(stub_instance, "send_command")


def test_my_DWX_Connector_wrapper_has__call__method(stub_instance):
    assert callable(stub_instance)


@pytest.fixture
def stub_instance():
    return DWX_ZeroMQ_Connector_STUB()


@pytest.fixture
def irrelevant_ticket():
    return 9876543210


@pytest.fixture
def irrelevant_symbol():
    return "irrelevant_symbol"


@pytest.fixture
def irrelevant_lots():
    return 1


@pytest.fixture
def irrelevant_price():
    return 1000


@pytest.fixture
def irrelevant_sl():
    return 2


@pytest.fixture
def irrelevant_tp():
    return 2


@pytest.mark.parametrize("order_type", list(ORDER_TYPE))
def test_ORDER_TYPE__str__conversion_looks_like_int(order_type):
    """Make sure that the __str__ method for out IntEnum subclass gives something that
    actually looks like an int, e.g. '1'."""
    assert int(str(order_type)) == order_type
    assert int("{}".format(order_type)) == order_type


@pytest.mark.parametrize("action", [ACTION.POS_MODIFY, ACTION.ORD_MODIFY])
def test_MODIFY_sl_and_tp_default_to_unchanged(action, irrelevant_ticket):
    cmd = command(action, ticket=irrelevant_ticket)
    assert cmd["_SL"] == -1
    assert cmd["_TP"] == -1
    cmd = command(action, ticket=irrelevant_ticket, sl=0)
    assert cmd["_SL"] == 0
    assert cmd["_TP"] == -1
    cmd = command(action, ticket=irrelevant_ticket, tp=10)
    assert cmd["_SL"] == -1
    assert cmd["_TP"] == 10


@pytest.mark.parametrize("order_type", [ORDER_TYPE.BUY, ORDER_TYPE.SELL])
def test_market_orders(
    order_type, irrelevant_symbol, irrelevant_lots, irrelevant_sl, irrelevant_tp
):
    order_dict = command(
        order_type,
        symbol=irrelevant_symbol,
        lots=irrelevant_lots,
        sl=irrelevant_sl,
        tp=irrelevant_tp,
    )
    assert isinstance(order_dict["_action"], int)
    assert order_dict["_action"] == ACTION.POS_OPEN
    assert isinstance(order_dict["_type"], int)
    assert order_dict["_type"] == order_type


@pytest.mark.parametrize("order_type", [ORDER_TYPE.BUY_LIMIT, ORDER_TYPE.SELL_LIMIT])
def test_limit_orders(
    order_type,
    irrelevant_symbol,
    irrelevant_lots,
    irrelevant_price,
    irrelevant_sl,
    irrelevant_tp,
):
    order_dict = command(
        order_type,
        symbol=irrelevant_symbol,
        lots=irrelevant_lots,
        price=irrelevant_price,
        sl=irrelevant_sl,
        tp=irrelevant_tp,
    )
    assert isinstance(order_dict["_action"], int)
    assert order_dict["_action"] == ACTION.ORD_OPEN


def test_command_fails_on_non_ORDER_TYPE(irrelevant_symbol, irrelevant_lots):
    with pytest.raises(RuntimeError):
        command(0, symbol=irrelevant_symbol, lots=irrelevant_lots)


@pytest.mark.parametrize("action", [ACTION.GET_DATA, ACTION.GET_TICK_DATA])
def test_not_implemented_ACTIONs(action):
    with pytest.raises(NotImplementedError):
        command(action)


def test__used_compArray_indices_by_action():
    """Although each compArray send by ZMQ from python to MT5 has length 10, not all 10
    of the elements of each compArray get actually processed by the DWX MT5 code. The
    _used_compArray_indices_by_action dictionary maps each action to the subset of
    range(10) representing indices of compArray that actually get used by the MT5 code.
    The idea is to require via our interface that the keyword arguments corresponding
    to these indices are supplied explicitly by the client."""
    for action in ACTION:
        assert action in my_interface._used_compArray_indices_by_action
    assert (
        my_interface._used_compArray_indices_by_action[ACTION.GET_DATA]
        is NotImplementedError
    )


def test_POS_OPEN_price_defaults_to_0(irrelevant_symbol, irrelevant_lots):
    kwargs = dict(symbol=irrelevant_symbol, lots=irrelevant_lots)

    with catch_warnings(record=True) as w:
        d = command(ORDER_TYPE.BUY, price=123, **kwargs)
        assert d["_price"] == 123
        assert len(w) == 3
        assert (
            str(w[0].message)
            == "We recommend using the default price==0 to execute at mkt price."
        )
        assert str(w[1].message) == "We recommend using a stoploss!"
        assert str(w[2].message) == "We recommend using a takeprofit!"

    # price==0 warning goes away
    with catch_warnings(record=True) as w:
        d = command(ORDER_TYPE.BUY, price=0, **kwargs)
        assert len(w) == 2
    assert d["_price"] == 0.0
    # price==0 warning goes away
    with catch_warnings(record=True) as w:
        d = command(ORDER_TYPE.BUY, **kwargs)
        assert len(w) == 2
    assert d["_price"] == 0.0


@pytest.mark.parametrize(
    "action",
    [
        ACTION.HEARTBEAT,
        ACTION.POS_CLOSE_ALL,
        ACTION.ORD_DELETE_ALL,
        ACTION.GET_POSITIONS,
        ACTION.GET_PENDING_ORDERS,
    ],
)
def test_simple_actions(action):
    assert command(action) == {
        "_action": action,
        "_type": "",
        "_symbol": "",
        "_price": "",
        "_SL": "",
        "_TP": "",
        "_comment": "",
        "_lots": "",
        "_magic": "",
        "_ticket": "",
    }


"""
     If compArray[0] = ACTION: one from [POS_OPEN,POS_MODIFY,POS_CLOSE,
        POS_CLOSE_PARTIAL,POS_CLOSE_MAGIC,POS_CLOSE_ALL,ORD_OPEN,ORD_MODIFY,ORD_DELETE,ORD_DELETE_ALL]
        compArray[1] = TYPE: one from [ORDER_TYPE_BUY,ORDER_TYPE_SELL only used when ACTION=POS_OPEN]
        or from [ORDER_TYPE_BUY_LIMIT,ORDER_TYPE_SELL_LIMIT,ORDER_TYPE_BUY_STOP,
        ORDER_TYPE_SELL_STOP only used when ACTION=ORD_OPEN]

        ORDER TYPES:
        https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type

        ORDER_TYPE_BUY = 0
        ORDER_TYPE_SELL = 1
        ORDER_TYPE_BUY_LIMIT = 2
        ORDER_TYPE_SELL_LIMIT = 3
        ORDER_TYPE_BUY_STOP = 4
        ORDER_TYPE_SELL_STOP = 5

        In this version ORDER_TYPE_BUY_STOP_LIMIT, ORDER_TYPE_SELL_STOP_LIMIT
        and ORDER_TYPE_CLOSE_BY are ignored.

        compArray[2] = Symbol (e.g. EURUSD, etc.)
        compArray[3] = Open/Close Price (ignored if ACTION = POS_MODIFY|ORD_MODIFY)
        compArray[4] = SL
        compArray[5] = TP
        compArray[6] = Trade Comment
        compArray[7] = Lots
        compArray[8] = Magic Number
        compArray[9] = Ticket Number (all type of modify|close|delete)
"""


def test_POS_CLOSE_requires_ticket():
    with pytest.raises(TypeError) as excinfo:
        command(ACTION.POS_CLOSE)


# // Only simple number to process
#    ENUM_DWX_SERV_ACTION switch_action=(ENUM_DWX_SERV_ACTION)StringToInteger(compArray[0]);

#    /* Setup processing variables */
#    string zmq_ret="";
#    string ret = "";
#    int ticket = -1;
#    bool ans=false;

#    /****************************
#    * PERFORM SOME CHECKS HERE *
#    ****************************/
#    if(CheckOpsStatus(pSocket,(int)switch_action)==true)
#      {
#       switch(switch_action)
#         {
#          case HEARTBEAT:

#             InformPullClient(pSocket,"{'_action': 'heartbeat', '_response': 'loud and clear!'}");
#             break;

#          case POS_OPEN:

#             zmq_ret="{";
#             ticket=DWX_PositionOpen(compArray[2],(int)StringToInteger(compArray[1]),StringToDouble(compArray[7]),
#                                     StringToDouble(compArray[3]),(int)StringToInteger(compArray[4]),(int)StringToInteger(compArray[5]),
#                                     compArray[6],(int)StringToInteger(compArray[8]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");
#             break;

#          case POS_MODIFY:

#             zmq_ret="{'_action': 'POSITION_MODIFY'";
#             ans=DWX_PositionModify((int)StringToInteger(compArray[9]),StringToDouble(compArray[4]),StringToDouble(compArray[5]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case POS_CLOSE:

#             zmq_ret="{";
#             DWX_PositionClose_Ticket((int)StringToInteger(compArray[9]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case POS_CLOSE_PARTIAL:

#             zmq_ret="{";
#             ans=DWX_PositionClosePartial(StringToDouble(compArray[7]),zmq_ret,(int)StringToInteger(compArray[9]));
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case POS_CLOSE_MAGIC:

#             zmq_ret="{";
#             DWX_PositionClose_Magic((int)StringToInteger(compArray[8]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case POS_CLOSE_ALL:

#             zmq_ret="{";
#             DWX_PositionsClose_All(zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case ORD_OPEN:

#             zmq_ret="{";
#             ticket=DWX_OrderOpen(compArray[2],(int)StringToInteger(compArray[1]),StringToDouble(compArray[7]),
#                                  StringToDouble(compArray[3]),(int)StringToInteger(compArray[4]),(int)StringToInteger(compArray[5]),
#                                  compArray[6],(int)StringToInteger(compArray[8]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case ORD_MODIFY:

#             zmq_ret="{'_action': 'ORDER_MODIFY'";
#             ans=DWX_OrderModify((int)StringToInteger(compArray[9]),StringToDouble(compArray[4]),StringToDouble(compArray[5]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case ORD_DELETE:

#             zmq_ret="{";
#             DWX_PendingOrderDelete_Ticket((int)StringToInteger(compArray[9]),zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case ORD_DELETE_ALL:

#             zmq_ret="{";
#             DWX_PendingOrderDelete_All(zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case GET_POSITIONS:

#             zmq_ret="{";
#             DWX_GetOpenPositions(zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case GET_PENDING_ORDERS:

#             zmq_ret="{";
#             DWX_GetPendingOrders(zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case GET_DATA:

#             zmq_ret="{";
#             DWX_GetData(compArray,zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          case GET_TICK_DATA:

#             zmq_ret="{";
#             DWX_GetTickData(compArray,zmq_ret);
#             InformPullClient(pSocket,zmq_ret+"}");

#             break;
#          default:
#             break;
#         }
#      }

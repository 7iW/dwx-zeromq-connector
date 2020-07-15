# stdlib
import copy
from enum import IntEnum
from warnings import warn
from typing import Union, Optional, NewType, Dict, List
from abc import ABC, abstractmethod

"""
    ORDER TYPES: 
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type
"""

from . import my_DWX_ZeroMQ_Connector_v1_0 as _DWX_Connector_module_
from .my_DWX_ZeroMQ_Connector_v1_0 import DWX_ZeroMQ_Connector


class ORDER_TYPE(IntEnum):
    """Taken from DWX_ZeroMQ_Connector_v1_0.py"""

    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5

    def __str__(self):
        return str(int(self.value))


# compArray[0] = ACTION
class ACTION(IntEnum):
    """Taken from DWX_ZeroMQ_Connector_v1_0.py"""

    HEARTBEAT = _DWX_Connector_module_.HEARTBEAT
    POS_OPEN = _DWX_Connector_module_.POS_OPEN
    POS_MODIFY = _DWX_Connector_module_.POS_MODIFY
    POS_CLOSE = _DWX_Connector_module_.POS_CLOSE
    POS_CLOSE_PARTIAL = _DWX_Connector_module_.POS_CLOSE_PARTIAL
    POS_CLOSE_MAGIC = _DWX_Connector_module_.POS_CLOSE_MAGIC
    POS_CLOSE_ALL = _DWX_Connector_module_.POS_CLOSE_ALL
    ORD_OPEN = _DWX_Connector_module_.ORD_OPEN
    ORD_MODIFY = _DWX_Connector_module_.ORD_MODIFY
    ORD_DELETE = _DWX_Connector_module_.ORD_DELETE
    ORD_DELETE_ALL = _DWX_Connector_module_.ORD_DELETE_ALL
    GET_POSITIONS = _DWX_Connector_module_.GET_POSITIONS
    GET_PENDING_ORDERS = _DWX_Connector_module_.GET_PENDING_ORDERS
    GET_DATA = _DWX_Connector_module_.GET_DATA
    GET_TICK_DATA = _DWX_Connector_module_.GET_TICK_DATA

    def __str__(self):
        return str(int(self.value))


class TicketTrackerMixin(DWX_ZeroMQ_Connector):
    """Keep track of the ticket of the most recent order with the `ticket` property."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not hasattr(self, "_ticket")
        self._ticket = None

    def _set_response_(self, _resp=None):
        if isinstance(_resp, dict):
            if "_ticket" in _resp:
                self._ticket = _resp["_ticket"]
        super()._set_response_(_resp)

    @property
    def ticket(self):
        if self._ticket is not None:
            return self._ticket
        else:
            return None


class PositionsTrackerMixin(DWX_ZeroMQ_Connector):
    """Keep track of recent positions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not hasattr(self, "_positions")
        self._positions = None

    def _set_response_(self, _resp=None):
        if isinstance(_resp, dict):
            if "_positions" in _resp:
                self._positions = ps = copy.deepcopy(_resp["_positions"])
                for position in ps:
                    if "_type" in ps[position]:
                        ps[position]["_type"] = ORDER_TYPE(ps[position]["_type"])
        super()._set_response_(_resp)

    @property
    def positions(self):
        return self._positions


class OrdersTrackerMixin(DWX_ZeroMQ_Connector):
    """Keep track of recent orders."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not hasattr(self, "_orders")
        self._orders = None

    def _set_response_(self, _resp=None):
        if isinstance(_resp, dict):
            if "_orders" in _resp:
                self._orders = _resp["_orders"]
        super()._set_response_(_resp)

    @property
    def orders(self):
        if self._orders is not None:
            p = copy.deepcopy(self._orders)
            for order in p:
                if "_type" in p[order]:
                    p[order]["_type"] = ORDER_TYPE(p[order]["_type"])
            return p
        else:
            return None


class DirectMethodAccessMixin(ABC):
    """We want to be able to access ACTIONs and ORDER_TYPEs via methods."""
    @abstractmethod
    def __call__(self, action_or_order_type: Union[ACTION, ORDER_TYPE], **kwargs):
        ...

    def HEARTBEAT(self, **kwargs):
        return self(ACTION.HEARTBEAT, **kwargs)

    def POS_OPEN(self, **kwargs):
        return self(ACTION.POS_OPEN, **kwargs)

    def POS_MODIFY(self, **kwargs):
        return self(ACTION.POS_MODIFY, **kwargs)

    def POS_CLOSE(self, **kwargs):
        return self(ACTION.POS_CLOSE, **kwargs)

    def POS_CLOSE_PARTIAL(self, **kwargs):
        return self(ACTION.POS_CLOSE_PARTIAL, **kwargs)

    def POS_CLOSE_MAGIC(self, **kwargs):
        return self(ACTION.POS_CLOSE_MAGIC, **kwargs)

    def POS_CLOSE_ALL(self, **kwargs):
        return self(ACTION.POS_CLOSE_ALL, **kwargs)

    def ORD_OPEN(self, **kwargs):
        return self(ACTION.ORD_OPEN, **kwargs)

    def ORD_MODIFY(self, **kwargs):
        return self(ACTION.ORD_MODIFY, **kwargs)

    def ORD_DELETE(self, **kwargs):
        return self(ACTION.ORD_DELETE, **kwargs)

    def ORD_DELETE_ALL(self, **kwargs):
        return self(ACTION.ORD_DELETE_ALL, **kwargs)

    def GET_POSITIONS(self, **kwargs):
        return self(ACTION.GET_POSITIONS, **kwargs)

    def GET_PENDING_ORDERS(self, **kwargs):
        return self(ACTION.GET_PENDING_ORDERS, **kwargs)

    def GET_DATA(self, **kwargs):
        return self(ACTION.GET_DATA, **kwargs)

    def GET_TICK_DATA(self, **kwargs):
        return self(ACTION.GET_TICK_DATA, **kwargs)

    def BUY(self, **kwargs):
        return self(ORDER_TYPE.BUY, **kwargs)

    def SELL(self, **kwargs):
        return self(ORDER_TYPE.SELL, **kwargs)

    def BUY_LIMIT(self, **kwargs):
        return self(ORDER_TYPE.BUY_LIMIT, **kwargs)

    def SELL_LIMIT(self, **kwargs):
        return self(ORDER_TYPE.SELL_LIMIT, **kwargs)

    def BUY_STOP(self, **kwargs):
        return self(ORDER_TYPE.BUY_STOP, **kwargs)

    def SELL_STOP(self, **kwargs):
        return self(ORDER_TYPE.SELL_STOP, **kwargs)

Command = NewType("Command", Dict)

class CommandGenerator(DirectMethodAccessMixin):
    """Just a class that can be used to generate command dicts to be passed to mt5"""
    def __call__(self, *args, **kwargs) -> Command:
        cmd: Command = command(*args, **kwargs)
        return cmd

class DWX_Connector(
    TicketTrackerMixin,
    PositionsTrackerMixin,
    OrdersTrackerMixin,
    DirectMethodAccessMixin,
    DWX_ZeroMQ_Connector,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_command(self, cmd: Command):
        """Take a command dict, send it to MT5."""
        self._DWX_MTX_SEND_COMMAND_(**cmd)

    def __call__(self, *args, **kwargs):
        """Functional composition: `send_command ∘ command`.
           Here `command` refers to the function defined later in this module.
        """
        cmd = command(*args, **kwargs)
        return self.send_command(cmd)

def command(action_or_order_type: Union[ACTION, ORDER_TYPE], **kwargs) -> Command:
    assert "type" not in kwargs, "Passing 'type' as a keyword arg is not supported."
    assert "action" not in kwargs, "Passing 'action' as a keyword arg is not supported."
    # Process the positional argument
    if isinstance(action_or_order_type, ORDER_TYPE):
        # If an order type is given, we deduce that action must be POS_OPEN or ORD_OPEN.
        _order_type = action_or_order_type
        if _order_type in [ORDER_TYPE.BUY, ORDER_TYPE.SELL]:
            action = ACTION.POS_OPEN
        elif _order_type in [
            ORDER_TYPE.BUY_LIMIT,
            ORDER_TYPE.SELL_LIMIT,
            ORDER_TYPE.BUY_STOP,
            ORDER_TYPE.SELL_STOP,
        ]:
            action = ACTION.ORD_OPEN
        else:
            raise ValueError("Got unexpected order type {}".format(repr(_order_type)))
        kwargs["type"] = _order_type
    elif isinstance(action_or_order_type, ACTION):
        action = action_or_order_type
        if action in [ACTION.GET_DATA, ACTION.GET_TICK_DATA]:
            raise NotImplementedError
    else:
        raise RuntimeError(
            "must have isinstance(order_type, Union[ACTION, ORDER_TYPE])"
        )
    kwargs["action"] = action

    # Check to see if an order is to be opened at market price.
    if action == ACTION.POS_OPEN:
        if "price" in kwargs:
            if kwargs["price"] != 0:
                warn("We recommend using the default price==0 to execute at mkt price.")
        else:
            kwargs["price"] = 0.0  # The default for POS_OPEN: mkt price execution.

    # Get required dict keys, and fill in defaults dict values if missing
    required_dict_keys = _required_dict_keys_by_action(action)
    if "sl" in required_dict_keys:
        if "sl" not in kwargs:
            if action in [ACTION.POS_OPEN, ACTION.ORD_OPEN]:
                # The default sl==0.0 means "no stoploss"
                kwargs["sl"] = 0.0
                warn("We recommend using a stoploss!")
            elif action in [ACTION.POS_MODIFY, ACTION.ORD_MODIFY]:
                # The default sl==-1 means "same stoploss"
                kwargs["sl"] = -1
    if "tp" in required_dict_keys:
        if "tp" not in kwargs:
            if action in [ACTION.POS_OPEN, ACTION.ORD_OPEN]:
                # The default tp==0.0 means "no takeprofit"
                kwargs["tp"] = 0.0
                warn("We recommend using a takeprofit!")
            elif action in [ACTION.POS_MODIFY, ACTION.ORD_MODIFY]:
                # The default tp==-1 means "same stoploss"
                kwargs["tp"] = -1
    if "comment" in required_dict_keys:
        if "comment" not in kwargs:
            kwargs["comment"] = ""
    if "magic" in required_dict_keys:
        if "magic" not in kwargs:
            kwargs["magic"] = 123456

    # Make sure that all required dict keys are present:
    for key in required_dict_keys:
        if key not in kwargs:
            raise TypeError(
                "Missing required key '{}' for action {}".format(key, repr(action))
            )
    # Make sure no extra dict keys are present
    for key in kwargs:
        if key not in required_dict_keys:
            raise TypeError(
                "Got unexpected keyword argument '{}' for action {}".format(
                    key, repr(action)
                )
            )
    return Command({
        "_action": kwargs[
            "action"
        ],  # '_action' is the only key that's always required.
        "_type": kwargs.get("type", ""),
        "_symbol": kwargs.get("symbol", ""),
        "_price": kwargs.get("price", ""),
        "_SL": kwargs.get("sl", ""),
        "_TP": kwargs.get("tp", ""),
        "_comment": kwargs.get("comment", ""),
        "_lots": kwargs.get("lots", ""),
        "_magic": kwargs.get("magic", ""),
        "_ticket": kwargs.get("ticket", ""),
    })


def _required_dict_keys_by_action(action):
    compArray_indices = _used_compArray_indices_by_action[action]
    return [
        [
            "action",
            "type",
            "symbol",
            "price",
            "sl",
            "tp",
            "comment",
            "lots",
            "magic",
            "ticket",
        ][idx]
        for idx in compArray_indices
    ]


# TODO: once python 3.9 comes out with the frozenmap feature, change this to a frozenmap.
_used_compArray_indices_by_action: Dict[ACTION, List[int]] = {
    ACTION.HEARTBEAT: [0,],
    #          case HEARTBEAT:
    ACTION.POS_OPEN: [0, 2, 1, 7, 3, 4, 5, 6, 8,],
    #          case POS_OPEN:
    # compArray[2]
    # (int)StringToInteger(compArray[1])
    # StringToDouble(compArray[7]),
    # StringToDouble(compArray[3])
    # (int)StringToInteger(compArray[4])
    # (int)StringToInteger(compArray[5]),
    # compArray[6]
    # (int)StringToInteger(compArray[8])
    ACTION.POS_MODIFY: [0, 9, 4, 5,],
    #          case POS_MODIFY:
    # (int)StringToInteger(compArray[9])
    # StringToDouble(compArray[4])
    # StringToDouble(compArray[5])
    ACTION.POS_CLOSE: [0, 9],
    # case POS_CLOSE:
    #    (int)StringToInteger(compArray[9])
    ACTION.POS_CLOSE_PARTIAL: [0, 7, 9],
    # case POS_CLOSE_PARTIAL:
    #    ACTION.StringToDouble(compArray[7])
    #    (int)StringToInteger(compArray[9]))
    ACTION.POS_CLOSE_MAGIC: [0, 8],
    # case POS_CLOSE_MAGIC:
    #    (int)StringToInteger(compArray[8])
    ACTION.POS_CLOSE_ALL: [0,],
    # case POS_CLOSE_ALL:
    ACTION.ORD_OPEN: [0, 2, 1, 7, 3, 4, 5, 6, 8,],
    # case ORD_OPEN:
    #    ACTION.compArray[2]
    #    (int)StringToInteger(compArray[1])
    #    ACTION.StringToDouble(compArray[7])
    #    ACTION.StringToDouble(compArray[3])
    #    (int)StringToInteger(compArray[4])
    #    (int)StringToInteger(compArray[5])
    #    ACTION.compArray[6]
    #    (int)StringToInteger(compArray[8])
    ACTION.ORD_MODIFY: [0, 9, 4, 5],
    # case ORD_MODIFY:
    #    (int)StringToInteger(compArray[9])
    #    ACTION.StringToDouble(compArray[4])
    #    ACTION.StringToDouble(compArray[5])
    ACTION.ORD_DELETE: [0, 9],
    # case ORD_DELETE:
    #    (int)StringToInteger(compArray[9])
    ACTION.ORD_DELETE_ALL: [0,],
    # case ORD_DELETE_ALL:
    ACTION.GET_POSITIONS: [0,],
    # case GET_POSITIONS:
    ACTION.GET_PENDING_ORDERS: [0,],
    # case GET_PENDING_ORDERS:
    ACTION.GET_DATA: NotImplementedError,  # type: ignore
    # case GET_DATA:
    #    ACTION.compArray
    ACTION.GET_TICK_DATA: NotImplementedError,  # type: ignore
    # case GET_TICK_DATA:
    #    ACTION.compArray
}

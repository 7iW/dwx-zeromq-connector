from warnings import warn
from enum import IntEnum
from typing import Union, Optional

"""
    ORDER TYPES: 
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type
"""

import my_DWX_ZeroMQ_Connector_v1_0 as _DWX_Connector_module_


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

class DWX_Connector(_DWX_Connector_module_.DWX_ZeroMQ_Connector):
    def send_command(self, command: dict):
        return self._DWX_MTX_SEND_COMMAND_(**command)
    def make_and_send_command(self, *args, **kwargs):
        cmd = command(*args, **kwargs)
        return self.send_command(cmd)

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


def command(action_or_order_type: Union[ACTION, ORDER_TYPE], **kwargs):
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
            # The default sl==0.0 means "no stoploss" for POS_OPEN/ORD_OPEN, and "same
            # stoploss" for POS_MODIFY/ORD_MODIFY
            kwargs["sl"] = 0.0
            if action in [ACTION.ORD_OPEN, ACTION.POS_OPEN]:
                warn("We recommend using a stoploss!")
    if "tp" in required_dict_keys:
        if "tp" not in kwargs:
            # The default tp==0.0 means "no takeprofit" for POS_OPEN/ORD_OPEN, and "same
            # takeprofit" for POS_MODIFY/ORD_MODIFY
            kwargs["tp"] = 0.0
            if action in [ACTION.ORD_OPEN, ACTION.POS_OPEN]:
                warn("We recommend using a takeprofit!")
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
    return {
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
    }


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
_used_compArray_indices_by_action = {
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
    ACTION.GET_DATA: NotImplementedError,
    # case GET_DATA:
    #    ACTION.compArray
    ACTION.GET_TICK_DATA: NotImplementedError,
    # case GET_TICK_DATA:
    #    ACTION.compArray
}

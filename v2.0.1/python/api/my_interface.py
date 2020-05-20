from enum import IntEnum

"""
    ORDER TYPES: 
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type
"""

import dwx


class ORDER_TYPE(IntEnum):
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5

    def __str__(self):
        return str(int(self.value))


# compArray[0] = ACTION
class ACTION:
    POS_OPEN = dwx.POS_OPEN
    POS_MODIFY = dwx.POS_MODIFY
    POS_CLOSE = dwx.POS_CLOSE
    POS_CLOSE_PARTIAL = dwx.POS_CLOSE_PARTIAL
    POS_CLOSE_MAGIC = dwx.POS_CLOSE_MAGIC
    POS_CLOSE_ALL = dwx.POS_CLOSE_ALL
    ORD_OPEN = dwx.ORD_OPEN
    ORD_MODIFY = dwx.ORD_MODIFY
    ORD_DELETE = dwx.ORD_DELETE
    ORD_DELETE_ALL = dwx.ORD_DELETE_ALL


def trade(
    order_type: ORDER_TYPE,
    *,
    symbol: str,
    price: float = 0.0,
    sl: float = 0.0,
    tp: float = 0.0,
    comment: str = "homestarruner_was_here",
    lots: float = 0.0,
    magic: int = 123456,
    ticket: int = 0,
):
    if not isinstance(order_type, ORDER_TYPE):
        raise RuntimeError("must have isinstance(order_type, ORDER_TYPE)")
    order_dict = {
        "_type": order_type,
        "_symbol": symbol,
        "_price": price,
        "_SL": sl,
        "_TP": tp,
        "_comment": comment,
        "_lots": lots,
        "_magic": magic,
        "_ticket": ticket,
    }
    if order_type in [ORDER_TYPE.BUY, ORDER_TYPE.SELL]:
        order_dict["_action"] = ACTION.POS_OPEN
    elif order_type in [ORDER_TYPE.BUY_LIMIT, ORDER_TYPE.SELL_LIMIT]:
        order_dict["_action"] = ACTION.ORD_OPEN
    else:
        raise NotImplementedError
    return order_dict

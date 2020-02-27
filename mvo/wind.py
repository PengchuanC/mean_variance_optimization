from WindPy import w


def index_close_price(indexes: list, start: str, end: str):
    w.start()
    data = w.wsd(
        indexes, "close", start, end, "Period=M", usedf=True,
    )
    if data[0] != 0:
        raise RuntimeError(f"Wind接口错误，错误码{data[0]}")
    return data[1]


def fund_close_price(funds: list, start: str, end: str):
    w.start()
    ret = w.wsd(funds, "NAV_adj", start, end, "PriceAdj=F", usedf=True)
    if ret[0] != 0:
        raise RuntimeError(f"Wind接口错误，错误码{ret[0]}")
    return ret[1]

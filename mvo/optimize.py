import numpy as np
import pandas as pd

from scipy.optimize import minimize

from mvo.config import index_pool, index_limit, universe_limit
from mvo.wind import index_close_price


class OptimizeConfig(object):
    start_date = "2007-01-01"
    end_date = "2019-12-31"
    window = 3
    r = 0.015
    low_risk = 0.03

    def __init__(self, risk=0.02):
        self.risk = risk

    @property
    def bounds(self):
        if self.risk <= self.low_risk:
            cash = index_pool.get('cash')
            for c in cash:
                index_limit[c] = (0.05, 1)
        return index_limit


def indexes_from_index_pool():
    indexes = []
    for index_list in index_pool.values():
        indexes.extend(index_list)
    return indexes


def index_history():
    """指数收盘价序列"""
    start = OptimizeConfig.start_date
    end = OptimizeConfig.end_date
    indexes = indexes_from_index_pool()
    data = index_close_price(indexes, start, end)
    return data


def cov_and_r(data):
    """根据指数收盘价序列计算协方差矩阵和年化收益"""
    r = np.power(data.iloc[-1, :] / data.iloc[0, :], 12 / (len(data) - 1)) - 1
    change = data.pct_change().dropna(how='all')
    cov = change.cov()
    return cov, r


class Optimize(object):
    _data = None

    def __init__(self, risk):
        self.risk = risk
        self.oc = OptimizeConfig(risk=risk)

    @property
    def data(self):
        if self._data is not None:
            return self._data
        start = self.oc.start_date
        end = self.oc.end_date
        indexes = indexes_from_index_pool()
        self._data = index_close_price(indexes, start, end)
        return self._data

    @property
    def constraints(self):
        cons = (
            {"type": "eq", "fun": lambda x: sum(x) - 1},
            {"type": "ineq", "fun": lambda x: self.risk - self.volatility(x)},
        )
        return cons

    @property
    def bounds(self):
        b = self.oc.bounds
        b = [b.get(x, universe_limit) for x in self.data.columns]
        b = tuple(b)
        return b

    def volatility(self, w):
        cov, _ = cov_and_r(self.data)
        p_var = np.dot(w.T, np.dot(cov.values, w))
        p_std = np.sqrt(p_var) * np.sqrt(12)
        return p_std

    def annual_return(self, w):
        _, r = cov_and_r(self.data)
        return -sum(w * r)

    def run(self):
        x0 = np.array([1.0 / len(self.bounds)] * len(self.bounds))
        outcome = minimize(self.annual_return, x0=x0, constraints=self.constraints, bounds=self.bounds)
        w = outcome.x
        sigma = self.volatility(w)
        miu = - outcome.fun
        sharpe = (miu - self.oc.r) / sigma
        columns = ['miu', 'sigma', 'sharpe'] + list(self.data.columns)
        ret = [miu, sigma, sharpe]
        ret.extend(list(w))
        ret = pd.Series(ret, index=columns)
        return ret


class RollingOptimize(Optimize):
    _all_data = None
    date = None

    def __init__(self, risk):
        super().__init__(risk)

    @property
    def rolling_date(self):
        """获取滚动优化的日期序列"""
        window = self.oc.window
        length = window*12
        dates = list(self.all_data.index[-length:])
        return dates

    def set_date(self, date):
        """此函数用来更改self.data的数据"""
        self.date = date

    @property
    def all_data(self):
        if self._all_data is not None:
            return self._all_data
        start = self.oc.start_date
        end = self.oc.end_date
        indexes = indexes_from_index_pool()
        self._all_data = index_close_price(indexes, start, end)
        return self._all_data

    @property
    def data(self):
        data = self.all_data
        data = data[data.index <= self.date]
        return data

    def rolling_run(self):
        data = pd.DataFrame()
        dates = self.rolling_date
        for date in dates:
            self.set_date(date)
            ret = self.run()
            data[date] = ret
        origin = data.iloc[:, -1]
        data = data.T
        roll = data.mean()
        roll.mean = origin.mean
        roll.sigma = origin.sigma
        roll.sharpe = origin.sharpe
        return roll

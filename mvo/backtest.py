import math

import pandas as pd
import numpy as np

from scipy.stats import norm

from mvo.config import fund_pool, index_pool
from mvo.wind import fund_close_price


class BackTestConfig(object):
    start_date = "2017-01-01"
    end_date = "2019-12-31"
    init_money = 1000000
    pool = fund_pool
    r = 0.015

    def __init__(self, w: dict):
        self.weight = w


def weight_from_mvo(ret):
    """根据mvo模型优化的结果来获取权重"""
    data = {key: ret[value].sum() for key, value in index_pool.items()}
    return data


class BackTest(object):

    def __init__(self, w):
        self.btc = BackTestConfig(w)

    def asset_allocate(self):
        ret = {}
        for type_, fund_ in self.btc.pool.items():
            money = self.btc.init_money * self.btc.weight[type_]
            money_allocated = money / len(fund_)
            for f in fund_:
                ret[f] = money_allocated
        return ret

    def funds_from_fund_pool(self):
        funds = []
        for fund_list in self.btc.pool.values():
            funds.extend(fund_list)
        return funds

    @property
    def data(self):
        funds = self.funds_from_fund_pool()
        data = fund_close_price(funds, self.btc.start_date, self.btc.end_date)
        return data

    def run(self):
        allocate = self.asset_allocate()
        allocate = pd.Series(allocate)
        data = self.data
        init_price = data.iloc[0, :]
        share = allocate / init_price
        data_hist = data * share
        return data_hist


class Performance(object):
    def __init__(self, history, alpha=0.05):
        self.data = history
        self.pv = history.T.sum()
        self.alpha = alpha

    @staticmethod
    def max_drawback(net_value: list):
        """
        根据每日净值计算最大回撤
        :param net_value: 每日净值
        :return: 最大回撤
        """
        max_value = 1
        back = []
        for i in net_value:
            if i > max_value:
                max_value = i
            else:
                back.append(i / max_value - 1)
        return min(back)

    @staticmethod
    def performance(hist, risk_off=0.015):
        length = (hist.index[-1] - hist.index[0]).days
        r = hist[-1] / hist[0] - 1
        annual_return = np.power(hist[-1] / hist[0], 365 / length) - 1
        hist_change = hist.pct_change().dropna(how="any")
        sigma = hist_change.std() * math.sqrt(252)
        sharpe = (annual_return - risk_off) / sigma
        mmd = Performance.max_drawback(hist)
        return [r, annual_return, sigma, sharpe, mmd]

    @staticmethod
    def var_hist(hist_change, alpha=0.05):
        data = sorted(hist_change)
        p = np.percentile(data, alpha * 100, interpolation="midpoint")
        return p

    @staticmethod
    def cvar_hist(hist_change, alpha=0.05):
        data = sorted(hist_change)
        p = np.percentile(data, alpha * 100, interpolation="midpoint")
        data = [x for x in data if x < p]
        return sum(data) / len(data)

    @staticmethod
    def var(hist_change, alpha=0.05):
        mean = hist_change.mean()
        std = hist_change.std()
        z = norm.ppf(alpha, loc=mean, scale=std)
        return z

    @staticmethod
    def cvar(hist_change, alpha=0.05):
        mean = hist_change.mean()
        var = hist_change.var()
        std = hist_change.std()
        return mean - norm.pdf(norm.ppf(alpha)) / alpha * std

    def all_var(self, hist_change, alpha=0.05):
        var_h = self.var_hist(hist_change, alpha) * math.sqrt(252)
        cvar_h = self.cvar_hist(hist_change, alpha) * math.sqrt(252)
        var_ = self.var(hist_change, alpha) * math.sqrt(252)
        cvar_ = self.cvar(hist_change, alpha) * math.sqrt(252)
        return [var_h, cvar_h, var_, cvar_]

    def run(self):
        pv = self.pv
        pv_change = pv.pct_change().dropna(how="all")
        perf = self.performance(pv)
        all_var = self.all_var(hist_change=pv_change, alpha=self.alpha)
        perf = perf + all_var
        ret = pd.Series(perf)
        ret.index = [
            "累计收益",
            "年化收益",
            "年化波动",
            "夏普比",
            "最大回撤",
            "VaR(历史模拟)",
            "CVaR(历史模拟)",
            "VaR",
            "CVaR",
        ]
        ret = pd.DataFrame(ret).T
        return ret

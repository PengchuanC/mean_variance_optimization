from mvo.optimize import Optimize
from mvo.backtest import BackTest, weight_from_mvo, Performance


target_volatility = 0.12
print('根据预期风险，分析最优资产配置方案')
optimize = Optimize(target_volatility)
weight = optimize.run()
print('资产配置\n', weight)
weight = weight_from_mvo(weight)

print('按照资产配置方案，开始回测业绩')
bt = BackTest(w=weight)
hist = bt.run()
hist.plot()
performance = Performance(hist, 0.05)
perf = performance.run()
print('拟合业绩\n', perf)

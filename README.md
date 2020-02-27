# mean_variance_optimization
根据均值方差理论优化fof组合资产配比并进行回测

## 说明
根据个人风险偏好，可以计算个人在低于指定风险下，收益最高的资产配置组合，简单使用的话可以按照如下操作来运行

```bash
git clone [this project]
cd [current work director]
python -m mvo
```

## 参数
可以在`__main__.py`文件中修改`target_volatility`指标，也可以在`optimize.py`文件下`OptimizeConfig`类中修改优化参数，在`backtest.py`中的`BackTestConfig`类下修改回测参数

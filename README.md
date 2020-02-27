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


## `config.py`文件说明
配置文件

### 1.index_pool
资产配置的类型，大类包含四类，分别为**权益**、**固收**、**另类**和**现金**，
**权益类**又包含A股（大盘和中盘）、港股、转债，**固收类**包含利率债和AA企业债，
在主流指数成分内配置

### 2.universe_limit
为了保证资产分配的多样性，在优化时对全部资产做个统一的限制

### 3.index_limit
统一限制太过粗糙，此处进行精确限定，如必须保证现金资产比例不低于5%

### 4.fund_pool
最后fof组合底层的标的资产，即小f
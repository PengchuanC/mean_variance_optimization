# 配置文件


# 优化所用的资产池
index_pool = {
    'equity': ['H00300.CSI', 'H00905.CSI', '000832.CSI', 'HSI1.HI'],
    'fix_income': ['CBA00301.CS', 'CBA04001.CS'],
    'alter': ['AU9999.SGE'],
    'cash': ['H11025.CSI']
}


# 资产比例上下限限制
universe_limit = (0, 0.30)
index_limit = {
    'AU9999.SGE': (0, 0.10),
    'H11025.CSI': (0.05, 0.10),
}


# 底层基金池
fund_pool = {
    "equity": [
        "166005.OF",
        "163402.OF",
        "519712.OF",
        "000979.OF",
        "110011.OF",
        "100038.OF",
    ],
    "fix_income": ["485111.OF", "519669.OF", "000286.OF", "000191.OF", "110007.OF",],
    "alter": ["000216.OF"],
    "cash": ["482002.OF"],
}

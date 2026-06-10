# tests/test_validators.py
import pandas as pd
import pytest
from pipeline.sources import prices_yf, wasde, drought


def test_prices_rejects_empty():
    with pytest.raises(Exception):
        prices_yf.validate(pd.DataFrame())


def test_prices_accepts_good():
    prices_yf.validate(
        pd.DataFrame(
            {"Open": [1], "High": [1], "Low": [1], "Close": [1], "Volume": [1]}
        )
    )


def test_wasde_requires_corn():
    df = pd.DataFrame(
        {
            "Commodity": ["Wheat"],
            "Attribute": ["x"],
            "Value": [1],
            "MarketYear": ["2026"],
            "ReportDate": ["May 2026"],
        }
    )
    with pytest.raises(Exception):
        wasde.validate(df)


def test_drought_requires_cols():
    with pytest.raises(Exception):
        drought.validate(pd.DataFrame({"foo": [1]}))

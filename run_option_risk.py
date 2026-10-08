"""Standalone WTI producer hedge overlay: full revaluation, fixed vol scenarios."""
import argparse
import json
from pathlib import Path
import pandas as pd
from src.data import make_demo_prices
from src.option_pricing import costless_ceiling
from src.nonlinear import OptionLeg, full_revaluation_pnl
from src.var_models import historical_var, historical_es


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prices",help="CSV with date,CL=F; omitted means explicitly synthetic")
    p.add_argument("--output-dir",default="outputs/options_demo")
    a=p.parse_args();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    prices=pd.read_csv(a.prices,index_col="date",parse_dates=True) if a.prices else make_demo_prices()
    f=float(prices["CL=F"].iloc[-1]);changes=prices["CL=F"].diff().dropna().iloc[-250:]
    floor,subfloor,t,vol,r=.85*f,.65*f,1.,.4,.04
    ceiling=costless_ceiling(f,floor,t,vol,r)
    three=costless_ceiling(f,floor,t,vol,r,subfloor)
    q=100_000
    portfolios={"unhedged_producer_proxy":[],
                "collar":[OptionLeg("put",floor,q,t,vol),OptionLeg("call",ceiling,-q,t,vol)],
                "three_way":[OptionLeg("put",floor,q,t,vol),OptionLeg("put",subfloor,-q,t,vol),OptionLeg("call",three,-q,t,vol)]}
    rows=[];scenarios={}
    for name,legs in portfolios.items():
        pnl=full_revaluation_pnl(f,changes,legs,futures_barrels=q,rate=r)
        scenarios[name]=pnl
        rows.append(dict(book=name,var_99=historical_var(pd.Series(pnl)),es_99=historical_es(pd.Series(pnl))))
    pd.DataFrame(rows).to_csv(out/"full_revaluation_var.csv",index=False)
    pd.DataFrame(scenarios,index=changes.index).to_csv(out/"scenario_pnl.csv")
    (out/"assumptions.json").write_text(json.dumps(dict(data_class="public snapshot" if a.prices else "synthetic demo",
        forward=f,floor=floor,subfloor=subfloor,ceiling=ceiling,three_way_ceiling=three,
        maturity=t,volatility=vol,rate=r,barrels=q,horizon="1/252 year",scope="standalone WTI producer proxy; not combined with refiner book; fixed volatility"),indent=2)+"\n")


if __name__=="__main__":main()

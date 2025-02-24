import numpy as np
import QuantLib as ql

class asian_option_pricer():
    def __init__(self,seed=123):
        print('\ninitializing Asian option pricer')
        print(str(ql.Actual365Fixed()))
        if seed == None:
            self.seed = 0
            print()
        else:
            self.seed = seed
            print(f"seed: {self.seed}\n")

        self.rng = "pseudorandom" # could use "lowdiscrepancy"
        self.numPaths = 100000
    def day_count(self):
        return ql.Actual365Fixed()

    def asian_option_price(self,
        s,k,r,g,w,
        averaging_type,n_fixings,fixing_frequency,past_fixings,
        kappa,theta,rho,eta,v0,calculation_date
        ):
        s = float(s)
        k = float(k)
        r = float(r)
        g = float(g)

        
        if w == 'call':
            option_type = ql.Option.Call 
        elif w == 'put':
            option_type = ql.Option.Put
        t = n_fixings*fixing_frequency
        
        periods = np.arange(fixing_frequency,t+1,fixing_frequency).astype(int)
        fixing_periods = [ql.Period(int(p),ql.Days) for p in periods]
        fixing_dates = [calculation_date + p for p in fixing_periods]

        expiration_date = calculation_date + fixing_periods[-1]


        riskFreeTS = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date,float(r),self.day_count()))
        dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date,float(g),self.day_count()))

        hestonProcess = ql.HestonProcess(riskFreeTS, dividendTS, ql.QuoteHandle(ql.SimpleQuote(s)), v0, kappa, theta, eta, rho)
        hestonModel = ql.HestonModel(hestonProcess)
        vanillaPayoff = ql.PlainVanillaPayoff(option_type, float(k))
        europeanExercise = ql.EuropeanExercise(expiration_date)
        
        if averaging_type == 'geometric':
            geometric_engine = ql.MCDiscreteGeometricAPHestonEngine(hestonProcess, self.rng, requiredSamples=self.numPaths,seed=self.seed)
            geometricAverage = ql.Average().Geometric
            geometricRunningAccumulator = 1.0
            discreteGeometricAsianOption = ql.DiscreteAveragingAsianOption(
                geometricAverage, geometricRunningAccumulator, past_fixings,
                fixing_dates, vanillaPayoff, europeanExercise)
            discreteGeometricAsianOption.setPricingEngine(geometric_engine)
            geometric_price = float(discreteGeometricAsianOption.NPV())
            return geometric_price
            
        else:
            arithmetic_engine = ql.MCDiscreteArithmeticAPHestonEngine(hestonProcess, self.rng, requiredSamples=self.numPaths,seed=self.seed)
            arithmeticAverage = ql.Average().Arithmetic
            arithmeticRunningAccumulator = s
            discreteArithmeticAsianOption = ql.DiscreteAveragingAsianOption(
                arithmeticAverage, arithmeticRunningAccumulator, past_fixings, 
                fixing_dates, vanillaPayoff, europeanExercise)
            discreteArithmeticAsianOption.setPricingEngine(arithmetic_engine)
            arithmetic_price = float(discreteArithmeticAsianOption.NPV())
            return arithmetic_price


aop = asian_option_pricer()

for i in range(365*(2024-1900)):
    calculation_date = ql.Date.todaysDate() - ql.Period(i
        ,ql.Days)
    price =  aop.asian_option_price(1416.59, 709, 0.04, 0.0, 'call', 'geometric', 1, 180, 0, 0.233438, 0.082956, -1.0, 0.098497, 0.10662, calculation_date)
    print(f"{price} - {calculation_date}")
    if price == 0:
        print(calculation_date)
        break

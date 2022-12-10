import numpy as np
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as ticker
import math
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings("ignore")
plt.rc('figure', max_open_warning = 0)

class CSVBacktestHandler:
    
    '''Class for processing and plotting backtested performance against the performance of respective
        asset(s) for a given period. Assumes that this data was generated and stored in CSV format.'''
    
    def __init__(self, backtestCSVName: str, underlyingCSVName: str) -> None:
        
        '''Constructor takes in input two strings, representing the filenames of desired frames
            in (backtest,underlying) order.'''''
        
        if backtestCSVName[-4:] == '.csv':
            self._backtestReturns = pd.read_csv(backtestCSVName)
        else:
            self._backtestReturns = pd.read_csv((backtestCSVName + str('.csv')))
        
        if underlyingCSVName[-4:] == '.csv':
            self._underlyingReturns = pd.read_csv(underlyingCSVName)
            self._tickerSymbol = underlyingCSVName[:-18]
        else:
            self._underlyingReturns = pd.read_csv((underlyingCSVName + str('.csv')))
            self._tickerSymbol = underlyingCSVName[:-14]
        
        self._concatenatedFrames = self.composer()
    

    def roundDown(self, number: int, divisor: int) -> int:
        
        '''Method to be used in determination of spacing for x-axis major ticks in equity curve plot.'''

        return (math.floor(number / divisor) * divisor)


    def preAdjuster(self) -> list:
               
        '''Method used to make datasets compatible in terms of divisibility and what not.
            Also, locates indices where backtest returns are to be placed in the underlying series,
            and how far the spread between those indices must be.'''
           
        fullIndexSet = np.arange(0,(len(self._underlyingReturns)), math.floor(len(self._underlyingReturns)/len(self._backtestReturns)))
        numberOfExtraIndices = (len(fullIndexSet) - len(self._backtestReturns))
        indicesToBeRemoved = fullIndexSet[np.round(np.linspace(0, len(fullIndexSet)-1, numberOfExtraIndices)).astype(int)]
        indices = [i for i in fullIndexSet if i not in indicesToBeRemoved]
        
        return (indices)
    
    
    def adjuster(self) -> pd.DataFrame:
                
        '''Method for replacing index of original backtest series with newly required index spacing.'''

        self._backtestReturns['Index'] = self.preAdjuster()
        self._backtestReturns = self._backtestReturns.set_index(self._backtestReturns['Index'])
        del self._backtestReturns['Index']
        self._backtestReturns = self._backtestReturns.loc[:, ~self._backtestReturns.columns.str.contains('^Unnamed')]
        self._backtestReturns.columns = ['backtestReturns']
        
        return (self._backtestReturns)
        
            
    def composer(self) -> pd.DataFrame:
        
        '''Method for putting backtest and underlying frames together. Adds 0 to both the head and tail of backtested returns,
            so that interpolation will be possible. Also adds and computes two columns for two methods of interpolation.'''
        
        concatenatedFrames = pd.concat([self._underlyingReturns, self.adjuster()], axis=1)
        
        if (pd.isnull(concatenatedFrames.iloc[0,5])):
            concatenatedFrames.at[0,'backtestReturns'] = 0
        else:
            pass
        
        if (pd.isnull(concatenatedFrames.iloc[(len(concatenatedFrames)-1),5])):
            concatenatedFrames.at[(len(concatenatedFrames)-1),'backtestReturns'] = 0 
        else:
            pass
        
        concatenatedFrames['linearInterpolation'] = concatenatedFrames['backtestReturns'].cumsum().interpolate(method = 'linear')
        concatenatedFrames['cubicSplineInterpolation'] = concatenatedFrames['backtestReturns'].cumsum().interpolate(method = 'cubic')
        
        return (concatenatedFrames)


    def equityCurvePlot(self) -> None:
       
        '''Method for plotting cumulative percentage change data of backtested and underlying returns.'''

        ax1 = self._concatenatedFrames['cubicSplineInterpolation'].plot(color = 'navy',figsize = [14.275,9.525], label = ('Automated Performance Trading ' + self._tickerSymbol + ' [582 Trades]'), linewidth = .9)
        ax1 = self._concatenatedFrames['Close'].pct_change().cumsum().plot(color = 'black',figsize = [14.275,9.525], label = (self._tickerSymbol + ' Performance'), linewidth = .9)
        ax1.axhline(linewidth = 2, color = 'firebrick', zorder = 1)
        ax1.legend(loc = "upper left", fontsize = 8)
        ax1.title.set_text('Long System over ' + self._tickerSymbol + ' with Overnight Holding Periods Permitted, ' + str(self._underlyingReturns.Date.iloc[0]) + ' – ' + str(self._underlyingReturns.Date.iloc[-1]))
        ax1.set_xlabel('Units [1 min tick interval]')
        ax1.xaxis.set_major_locator(MultipleLocator(((self.roundDown(len(self._concatenatedFrames), 10000)) / 10)))
        ax1.yaxis.set_major_locator(MultipleLocator(.025))
        ax1.get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        yValues = ax1.get_yticks()
        ax1.set_yticklabels(['{:,.2%}'.format(y) for y in yValues])
        ax1.set_xlim(0, len(self._concatenatedFrames))
        ax1.minorticks_on()
        ax1.grid(which = 'both', linestyle = '-', linewidth = '1', color = 'dimgrey')
        ax1.grid(which = 'minor', linestyle = ':', linewidth = '1', color = 'grey')
        plt.pause(0.01)
        
        
    def equityCurveDistribution(self) -> None:
        
        '''Method for plotting distribution(s) of percentage change data for backtested and underlying returns.'''
        
        self._backtestReturns.hist(bins = 58, color = 'navy', grid = True, alpha = 0.6, orientation = 'vertical', figsize = [14.275,9.525], label = ('Automated Performance Trading ' + self._tickerSymbol + ' [582 Trades]'), linewidth = 1)
        self._underlyingReturns.Close[::58].pct_change().hist(bins = 58, color = 'black', grid = True, alpha = 0.4, orientation = 'vertical', figsize = [14.275,9.525],label = (self._tickerSymbol + ' Performance'), linewidth = 1)
        ax1 = plt.gca()
        ax1.legend(loc = "upper left", fontsize = 8)
        ax1.axvline(0, linewidth = 1.5, color = 'firebrick', zorder = 1)
        ax1.title.set_text('Long System over ' + self._tickerSymbol + ' with Overnight Holding Periods Permitted, ' + str(self._underlyingReturns.Date.iloc[0]) + ' – ' + str(self._underlyingReturns.Date.iloc[-1]))
        ax1.tick_params(labelsize = 16, labelright = True)
        ax1.minorticks_on()
        ax1.grid(which = 'both', linestyle = '-', linewidth = '1', color = 'dimgrey')
        ax1.grid(which = 'minor', linestyle = ':', linewidth = '1', color = 'grey')
        plt.pause(0.01)
        
        
backtestObject = CSVBacktestHandler('SPXBacktestOnSubset20220422.csv','SPXSubset20220422.csv')
backtestObject.equityCurvePlot()
backtestObject.equityCurveDistribution()

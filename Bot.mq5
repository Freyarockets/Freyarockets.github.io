//+------------------------------------------------------------------+
//|                                                 ThreeMA_Fib.mq5  |
//|                                  Copyright 2026, AI Trading Bot |
//|                                             https://mql5.com |
//|                           PROFESSIONAL RISK-MANAGED VERSION      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
#property link      "https://mql5.com"
#property version   "2.00"
#property strict

// Include the standard trade library
#include <Trade\Trade.mqh>
CTrade trade;

//--- Input parameters
input group "--- MA Settings ---"
input int                  InpFastMAPeriod   = 12;          // Fast MA Period (Signal)
input int                  InpMediumMAPeriod = 15;          // Medium MA Period (Filter)
input int                  InpSlowMAPeriod   = 17;          // Slow MA Period (Trend)
input ENUM_MA_METHOD       InpMAMethod       = MODE_SMA;    // MA Method
input ENUM_APPLIED_PRICE   InpMAPrice        = PRICE_CLOSE; // Applied Price

input group "--- Risk Management ---"
input double               InpRiskPercent    = 1.0;         // Risk per trade (% of account)
input double               InpStopLossPoints = 50;          // Stop Loss in points
input double               InpTakeProfitRatio = 2.0;         // Risk:Reward Ratio (TP = SL * ratio)
input double               InpMaxDrawdown    = 20.0;         // Max drawdown % to stop trading
input int                  InpMaxOpenTrades  = 1;           // Maximum concurrent positions

input group "--- Trade Settings ---"
input ulong                InpMagicNumber    = 123456;      // Magic Number
input double               InpMinLotSize     = 0.01;        // Minimum lot size
input bool                 InpTradeOnNewBar  = true;        // Only trade on new bar close

input group "--- Fibonacci Settings ---"
input bool                 InpDrawFibonacci  = true;         // Draw Fibonacci levels
input int                  InpFibLookback    = 30;          // Lookback bars for Fib

//--- Global Indicator Handles
int fastMAHandle;
int medMAHandle;
int slowMAHandle;

//--- Trade Statistics
struct TradeStats {
   double initialBalance;
   double highestBalance;
   double lastClosePrice;
   int winCount;
   int lossCount;
};

TradeStats stats;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Set expert magic number for order tracking
   trade.SetExpertMagicNumber(InpMagicNumber);
   
   // Initialize trade statistics
   stats.initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   stats.highestBalance = stats.initialBalance;
   stats.winCount = 0;
   stats.lossCount = 0;

   // Initialize Moving Average indicator handles
   fastMAHandle = iMA(_Symbol, _Period, InpFastMAPeriod, 0, InpMAMethod, InpMAPrice);
   medMAHandle  = iMA(_Symbol, _Period, InpMediumMAPeriod, 0, InpMAMethod, InpMAPrice);
   slowMAHandle = iMA(_Symbol, _Period, InpSlowMAPeriod, 0, InpMAMethod, InpMAPrice);

   // Validate indicator handles
   if(fastMAHandle == INVALID_HANDLE || medMAHandle == INVALID_HANDLE || slowMAHandle == INVALID_HANDLE)
   {
      Print("ERROR: Failed to create indicator handles.");
      return(INIT_FAILED);
   }

   Print("Bot initialized successfully. Initial Balance: ", stats.initialBalance);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release handles to optimize memory
   IndicatorRelease(fastMAHandle);
   IndicatorRelease(medMAHandle);
   IndicatorRelease(slowMAHandle);
   
   // Clean up Fibonacci chart objects
   ObjectsDeleteAll(0, "FibLevel_");
   
   Print("Bot deinitialized. Final Stats - Wins: ", stats.winCount, " | Losses: ", stats.lossCount);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check for new bar
   static datetime lastBarTime;
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   
   if(InpTradeOnNewBar && currentBarTime == lastBarTime) 
      return;
   
   // Update highest balance for drawdown calculation
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   if(currentBalance > stats.highestBalance) 
      stats.highestBalance = currentBalance;
   
   // Check drawdown limit
   if(!IsDrawdownAcceptable())
   {
      Print("WARNING: Maximum drawdown exceeded. Trading suspended.");
      return;
   }
   
   // Dynamic arrays to hold indicator values
   double fastMA[], medMA[], slowMA[];
   
   // Set indexing direction (true means index 0 is the newest)
   ArraySetAsSeries(fastMA, true);
   ArraySetAsSeries(medMA, true);
   ArraySetAsSeries(slowMA, true);

   // Copy indicator buffer data (using bar 1 to ensure closed candle)
   if(CopyBuffer(fastMAHandle, 0, 1, 3, fastMA) < 0 ||
      CopyBuffer(medMAHandle, 0, 1, 3, medMA) < 0 ||
      CopyBuffer(slowMAHandle, 0, 1, 3, slowMA) < 0)
   {
      Print("ERROR: Failed to copy indicator buffers.");
      return;
   }

   lastBarTime = currentBarTime;
   
   // Check for existing positions
   int openPositions = CountOpenPositions();
   if(openPositions >= InpMaxOpenTrades)
      return;
   
   // Get current market data
   double askPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bidPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = SymbolInfoDouble(_Symbol, SYMBOL_SPREAD);
   
   // Analyze Market Conditions
   bool isBullish = (fastMA[0] > medMA[0]) && (medMA[0] > slowMA[0]);
   bool isBearish = (fastMA[0] < medMA[0]) && (medMA[0] < slowMA[0]);
   bool signalCrossover = (fastMA[1] <= medMA[1]) && (fastMA[0] > medMA[0]);
   
   // Enter Long Position
   if(signalCrossover && isBullish)
   {
      ExecuteBuyTrade(askPrice, bidPrice);
      
      if(InpDrawFibonacci)
         DrawFibonacciLevels();
   }
   
   // Exit Conditions (managed through OnTradeTransaction)
   ManageOpenPositions();
}

//+------------------------------------------------------------------+
//| Execute Buy Trade with proper risk management                    |
//+------------------------------------------------------------------+
void ExecuteBuyTrade(double askPrice, double bidPrice)
{
   // Calculate stop loss and take profit
   double stopLossPoints = NormalizeDouble(InpStopLossPoints * _Point, _Digits);
   double stopLossPrice = NormalizeDouble(askPrice - stopLossPoints, _Digits);
   double takeProfitPrice = NormalizeDouble(askPrice + (stopLossPoints * InpTakeProfitRatio), _Digits);
   
   // Calculate lot size based on risk percentage
   double lotSize = CalculateLotSize(stopLossPoints);
   
   if(lotSize < InpMinLotSize)
   {
      Print("WARNING: Calculated lot size (", lotSize, ") is below minimum (", InpMinLotSize, ")");
      lotSize = InpMinLotSize;
   }
   
   // Normalize lot size to broker requirements
   lotSize = NormalizeLotSize(lotSize);
   
   // Place the order
   bool result = trade.Buy(lotSize, _Symbol, askPrice, stopLossPrice, takeProfitPrice, "3MA Buy Signal");
   
   if(result)
   {
      Print("BUY EXECUTED | Price: ", askPrice, " | SL: ", stopLossPrice, " | TP: ", takeProfitPrice, " | Lot: ", lotSize);
   }
   else
   {
      Print("ERROR: Buy order failed. Result: ", trade.ResultRetcode(), " | Description: ", trade.ResultRetcodeDescription());
   }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk percentage                      |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLossInPoints)
{
   if(stopLossInPoints <= 0) return InpMinLotSize;
   
   double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = accountBalance * (InpRiskPercent / 100.0);
   
   // Get pip value (for most pairs, 1 pip = 0.0001)
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   
   // Calculate lot size: Risk Amount / (Stop Loss Points * Pip Value)
   double pipValue = tickValue / tickSize;
   double lotSize = riskAmount / (stopLossInPoints / _Point * pipValue);
   
   return lotSize;
}

//+------------------------------------------------------------------+
//| Normalize lot size to broker requirements                        |
//+------------------------------------------------------------------+
double NormalizeLotSize(double lotSize)
{
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   if(lotSize < minLot) lotSize = minLot;
   if(lotSize > maxLot) lotSize = maxLot;
   
   lotSize = MathFloor(lotSize / lotStep) * lotStep;
   return lotSize;
}

//+------------------------------------------------------------------+
//| Count open positions with magic number                           |
//+------------------------------------------------------------------+
int CountOpenPositions()
{
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         count++;
   }
   return count;
}

//+------------------------------------------------------------------+
//| Manage open positions (trailing stops, partial exits)            |
//+------------------------------------------------------------------+
void ManageOpenPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!PositionSelectByTicket(PositionGetTicket(i)))
         continue;
      
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      
      if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber)
         continue;
      
      ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double posOpenPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double posSL = PositionGetDouble(POSITION_SL);
      double posTP = PositionGetDouble(POSITION_TP);
      double bidPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      
      // Implement trailing stop for long positions
      if(posType == POSITION_TYPE_BUY)
      {
         double profit = bidPrice - posOpenPrice;
         double trailingDistance = NormalizeDouble(InpStopLossPoints * 0.5 * _Point, _Digits);
         
         // Move SL up if price moves favorably
         if(profit > (InpStopLossPoints * _Point) && bidPrice - posSL > trailingDistance)
         {
            double newSL = NormalizeDouble(bidPrice - trailingDistance, _Digits);
            if(newSL > posSL)
            {
               trade.PositionModify(PositionGetTicket(i), newSL, posTP);
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Check if drawdown is acceptable                                  |
//+------------------------------------------------------------------+
bool IsDrawdownAcceptable()
{
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double drawdown = ((stats.highestBalance - currentBalance) / stats.highestBalance) * 100.0;
   
   return (drawdown <= InpMaxDrawdown);
}

//+------------------------------------------------------------------+
//| Draws Fibonacci Levels on the Chart                              |
//+------------------------------------------------------------------+
void DrawFibonacciLevels()
{
   // Find local market structure
   int highestBar = iHighest(_Symbol, _Period, MODE_HIGH, InpFibLookback, 1);
   int lowestBar  = iLowest(_Symbol, _Period, MODE_LOW, InpFibLookback, 1);
   
   double highPrice = iHigh(_Symbol, _Period, highestBar);
   double lowPrice  = iLow(_Symbol, _Period, lowestBar);
   
   datetime timeHigh = iTime(_Symbol, _Period, highestBar);
   datetime timeLow  = iTime(_Symbol, _Period, lowestBar);
   
   // Remove previous Fibonacci objects
   ObjectsDeleteAll(0, "FibLevel_");
   
   // Draw Standard Fibonacci Retracement Object
   string fibName = "FibLevel_Retracement";
   if(ObjectCreate(0, fibName, OBJ_FIBO, 0, timeLow, lowPrice, timeHigh, highPrice))
   {
      ObjectSetInteger(0, fibName, OBJPROP_COLOR, clrGoldenrod);
      ObjectSetInteger(0, fibName, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, fibName, OBJPROP_STYLE, STYLE_DASHDOT);
      ChartRedraw(0);
   }
}

//+------------------------------------------------------------------+
//| OnTrade event - track wins/losses                                |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &request, const MqlTradeResult &result)
{
   // Track when positions close
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
   {
      if(trans.symbol == _Symbol && trans.magic == InpMagicNumber)
      {
         MqlTradeCheckResult check;
         if(trans.deal_profit > 0)
         {
            stats.winCount++;
         }
         else if(trans.deal_profit < 0)
         {
            stats.lossCount++;
         }
         
         Print("Position Closed | P&L: ", trans.deal_profit, " | Wins: ", stats.winCount, " | Losses: ", stats.lossCount);
      }
   }
}

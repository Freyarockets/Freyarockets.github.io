//+------------------------------------------------------------------+
//|                                                 ThreeMA_Fib.mq5  |
//|                                  Copyright 2026, AI Trading Bot |
//|                                             https://mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
#property link      "https://mql5.com"
#property version   "1.00"
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

input group "--- Trade Settings ---"
input double               InpLotSize        = 0.1;         // Lot Size
input ulong                InpMagicNumber    = 123456;      // Magic Number

//--- Global Indicator Handles
int fastMAHandle;
int medMAHandle;
int slowMAHandle;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Set expert magic number for order tracking
   trade.SetExpertMagicNumber(InpMagicNumber);

   // Initialize Moving Average indicator handles
   fastMAHandle = iMA(_Symbol, _Period, InpFastMAPeriod, 0, InpMAMethod, InpMAPrice);
   medMAHandle  = iMA(_Symbol, _Period, InpMediumMAPeriod, 0, InpMAMethod, InpMAPrice);
   slowMAHandle = iMA(_Symbol, _Period, InpSlowMAPeriod, 0, InpMAMethod, InpMAPrice);

   // Validate indicator handles
   if(fastMAHandle == INVALID_HANDLE || medMAHandle == INVALID_HANDLE || slowMAHandle == INVALID_HANDLE)
   {
      Print("Failed to create indicator handles.");
      return(INIT_FAILED);
   }

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
   
   // Clean up any generated Fibonacci chart objects
   ObjectsDeleteAll(0, "FibLevel_");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check if a new bar has just opened to avoid multi-trading on one tick
   static datetime lastBarTime;
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if(currentBarTime == lastBarTime) return;
   
   // Dynamic arrays to hold indicator values
   double fastMA[], medMA[], slowMA[];
   
   // Set indexing direction (true means index 0 is the newest completed bar)
   ArraySetAsSeries(fastMA, true);
   ArraySetAsSeries(medMA, true);
   ArraySetAsSeries(slowMA, true);

   // Copy indicator buffer data (using bar 1 to ensure a fully closed candle)
   if(CopyBuffer(fastMAHandle, 0, 1, 2, fastMA) < 0 ||
      CopyBuffer(medMAHandle, 0, 1, 2, medMA) < 0 ||
      CopyBuffer(slowMAHandle, 0, 1, 2, slowMA) < 0)
   {
      Print("Error copying indicator buffers.");
      return;
   }

   // Update tracked bar time on successful copy
   lastBarTime = currentBarTime;

   // Check if we already have an open position for this bot
   if(PositionsTotal() > 0)
   {
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            // Position exists, skip execution to prevent over-exposure
            return; 
         }
      }
   }

   // Define Core Conditions
   // Condition: 12 MA is greater than 15 MA
   bool buyCondition = (fastMA[0] > medMA[0]);

   // Execute Market Buy Order
   if(buyCondition)
   {
      double askPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      trade.Buy(InpLotSize, _Symbol, askPrice, 0, 0, "3MA Execution");
      
      // Draw Fibonacci levels based on recent structural high and low
      DrawFibonacciLevels();
   }
}

//+------------------------------------------------------------------+
//| Draws Fibonacci Levels on the Chart from recent swing high/low   |
//+------------------------------------------------------------------+
void DrawFibonacciLevels()
{
   // Look back 30 bars to find local market structure
   int lookback = 30;
   int highestBar = iHighest(_Symbol, _Period, MODE_HIGH, lookback, 1);
   int lowestBar  = iLowest(_Symbol, _Period, MODE_LOW, lookback, 1);
   
   double highPrice = iHigh(_Symbol, _Period, highestBar);
   double lowPrice  = iLow(_Symbol, _Period, lowestBar);
   
   datetime timeHigh = iTime(_Symbol, _Period, highestBar);
   datetime timeLow  = iTime(_Symbol, _Period, lowestBar);
   
   // Remove previous Fibonacci objects to keep chart clean
   ObjectsDeleteAll(0, "FibLevel_");
   
   // Draw Standard Fibonacci Retracement Object
   string fibName = "FibLevel_Retracement";
   if(ObjectCreate(0, fibName, OBJ_FIBO, 0, timeLow, lowPrice, timeHigh, highPrice))
   {
      ObjectSetInteger(0, fibName, OBJPROP_COLOR, clrGoldenrod);
      ObjectSetInteger(0, fibName, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, fibName, OBJPROP_STYLE, STYLE_DASHDOT);
      
      // Force text descriptions to show on chart right-side
      ChartRedraw(0);
   }
}

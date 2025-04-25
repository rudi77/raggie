declare module 'recharts' {
  import * as React from 'react';

  export interface ResponsiveContainerProps {
    width?: number | string;
    height?: number | string;
    aspect?: number;
    minHeight?: number;
    children: React.ReactNode;
  }

  export interface LineChartProps {
    data?: any[];
    margin?: {
      top?: number;
      right?: number;
      bottom?: number;
      left?: number;
    };
    children: React.ReactNode;
  }

  export interface LineProps {
    type?: 'monotone' | 'linear' | 'step' | 'stepBefore' | 'stepAfter';
    dataKey: string;
    stroke?: string;
    strokeWidth?: number;
    dot?: any;
    activeDot?: any;
  }

  export interface XAxisProps {
    dataKey?: string;
    stroke?: string;
    tick?: any;
    tickLine?: any;
  }

  export interface YAxisProps {
    stroke?: string;
    tick?: any;
    tickLine?: any;
    tickFormatter?: (value: any) => string;
  }

  export interface CartesianGridProps {
    strokeDasharray?: string;
    stroke?: string;
    opacity?: number;
  }

  export interface TooltipProps {
    content?: React.ComponentType<any>;
  }

  export const ResponsiveContainer: React.FC<ResponsiveContainerProps>;
  export const LineChart: React.FC<LineChartProps>;
  export const Line: React.FC<LineProps>;
  export const XAxis: React.FC<XAxisProps>;
  export const YAxis: React.FC<YAxisProps>;
  export const CartesianGrid: React.FC<CartesianGridProps>;
  export const Tooltip: React.FC<TooltipProps>;
} 
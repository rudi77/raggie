import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';

interface LineChartWidgetProps {
  data: any[];
}

export const LineChartWidget: React.FC<LineChartWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Process data for the chart
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Get all keys except the first one (assuming first is x-axis)
    const keys = Object.keys(data[0]);
    const xAxisKey = keys[0];
    const dataKeys = keys.slice(1);

    return data.map(item => {
      const processedItem: any = {};
      processedItem[xAxisKey] = item[xAxisKey];
      
      dataKeys.forEach(key => {
        processedItem[key] = typeof item[key] === 'number' ? item[key] : parseFloat(item[key]);
      });
      
      return processedItem;
    });
  }, [data]);

  // Generate colors for lines
  const colors = useMemo(() => {
    const baseColors = [
      theme.palette.primary.main,
      theme.palette.secondary.main,
      theme.palette.error.main,
      theme.palette.warning.main,
      theme.palette.info.main,
      theme.palette.success.main
    ];
    
    const keys = Object.keys(data[0] || {}).slice(1);
    return keys.map((_, index) => baseColors[index % baseColors.length]);
  }, [data, theme]);

  if (!data || data.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100%"
        width="100%"
        minWidth="500px"
      >
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  const keys = Object.keys(data[0]).slice(1);

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      minWidth: '500px',
      backgroundColor: theme.palette.background.paper,
      borderRadius: theme.shape.borderRadius,
      boxShadow: theme.shadows[2],
      p: 2,
      '& .recharts-responsive-container': {
        minWidth: '500px !important',
        width: '100% !important'
      },
      '& .recharts-cartesian-grid-horizontal line, & .recharts-cartesian-grid-vertical line': {
        stroke: theme.palette.divider
      },
      '& .recharts-text': {
        fill: theme.palette.text.primary
      },
      '& .recharts-legend-item-text': {
        color: `${theme.palette.text.primary} !important`
      },
      '& .recharts-tooltip-wrapper': {
        outline: 'none'
      }
    }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 25,
          }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={theme.palette.divider}
            vertical={false}
          />
          <XAxis
            dataKey={Object.keys(data[0])[0]}
            tick={{ fill: theme.palette.text.primary }}
            stroke={theme.palette.divider}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            tick={{ fill: theme.palette.text.primary }}
            stroke={theme.palette.divider}
            width={60}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: theme.shape.borderRadius,
              boxShadow: theme.shadows[3],
              color: theme.palette.text.primary
            }}
            labelStyle={{ color: theme.palette.text.primary }}
            itemStyle={{ color: theme.palette.text.primary }}
            cursor={{ stroke: theme.palette.divider }}
          />
          <Legend 
            wrapperStyle={{ 
              paddingTop: '10px',
              color: theme.palette.text.primary
            }}
          />
          {keys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index]}
              strokeWidth={2}
              dot={false}
              activeDot={{ 
                r: 8,
                stroke: theme.palette.background.paper,
                strokeWidth: 2
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}; 
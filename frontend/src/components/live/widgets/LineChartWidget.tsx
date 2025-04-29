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
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  const keys = Object.keys(data[0]).slice(1);

  return (
    <Box sx={{ width: '100%', height: '100%', minHeight: 300 }}>
      <ResponsiveContainer>
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={Object.keys(data[0])[0]}
            tick={{ fill: theme.palette.text.primary }}
          />
          <YAxis tick={{ fill: theme.palette.text.primary }} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: theme.shape.borderRadius,
            }}
            labelStyle={{ color: theme.palette.text.primary }}
          />
          <Legend />
          {keys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index]}
              activeDot={{ r: 8 }}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}; 
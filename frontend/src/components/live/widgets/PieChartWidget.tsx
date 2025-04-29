import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';

interface PieChartWidgetProps {
  data: any[];
}

export const PieChartWidget: React.FC<PieChartWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Process data for the chart
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // For pie chart, we expect data in format [{name: string, value: number}]
    // If data is not in this format, we'll try to convert it
    if (data[0].hasOwnProperty('name') && data[0].hasOwnProperty('value')) {
      return data;
    }

    // Try to convert from other formats
    const keys = Object.keys(data[0]);
    if (keys.length >= 2) {
      // Use first key as name, second as value
      return data.map(item => ({
        name: String(item[keys[0]]),
        value: typeof item[keys[1]] === 'number' ? item[keys[1]] : parseFloat(item[keys[1]])
      }));
    }

    return [];
  }, [data]);

  // Generate colors for pie segments
  const colors = useMemo(() => {
    const baseColors = [
      theme.palette.primary.main,
      theme.palette.secondary.main,
      theme.palette.error.main,
      theme.palette.warning.main,
      theme.palette.info.main,
      theme.palette.success.main
    ];
    
    return chartData.map((_, index) => baseColors[index % baseColors.length]);
  }, [chartData, theme]);

  if (!data || data.length === 0 || chartData.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  // Calculate total for percentage display
  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  // Custom tooltip formatter
  const formatTooltip = (value: number) => {
    const percentage = ((value / total) * 100).toFixed(1);
    return `${value} (${percentage}%)`;
  };

  return (
    <Box sx={{ width: '100%', height: '100%', minHeight: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index]} />
            ))}
          </Pie>
          <Tooltip
            formatter={formatTooltip}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: theme.shape.borderRadius,
            }}
            labelStyle={{ color: theme.palette.text.primary }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
}; 
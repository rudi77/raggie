import React, { useMemo } from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface NumberWidgetProps {
  data: any;
}

export const NumberWidget: React.FC<NumberWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Process data for display
  const { value, previousValue, label, trend } = useMemo(() => {
    if (!data) {
      return { value: null, previousValue: null, label: '', trend: null };
    }

    // If data is a simple number or string
    if (typeof data === 'number' || typeof data === 'string') {
      return {
        value: typeof data === 'number' ? data : parseFloat(data),
        previousValue: null,
        label: '',
        trend: null
      };
    }

    // If data is an object with value property
    if (data.hasOwnProperty('value')) {
      const value = typeof data.value === 'number' ? data.value : parseFloat(data.value);
      const previousValue = data.previousValue ? 
        (typeof data.previousValue === 'number' ? data.previousValue : parseFloat(data.previousValue)) : 
        null;
      
      // Calculate trend if we have previous value
      let trend = null;
      if (previousValue !== null) {
        const diff = value - previousValue;
        const percentChange = (diff / Math.abs(previousValue)) * 100;
        
        if (Math.abs(percentChange) < 1) {
          trend = 'flat';
        } else if (diff > 0) {
          trend = 'up';
        } else {
          trend = 'down';
        }
      }

      return {
        value,
        previousValue,
        label: data.label || '',
        trend
      };
    }

    // If data is an array, use the first value
    if (Array.isArray(data) && data.length > 0) {
      const firstItem = data[0];
      const keys = Object.keys(firstItem);
      
      if (keys.length > 0) {
        const value = typeof firstItem[keys[0]] === 'number' ? 
          firstItem[keys[0]] : 
          parseFloat(firstItem[keys[0]]);
        
        return {
          value,
          previousValue: null,
          label: keys[0],
          trend: null
        };
      }
    }

    return { value: null, previousValue: null, label: '', trend: null };
  }, [data]);

  if (value === null) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  // Format the value based on its magnitude
  const formatValue = (val: number): string => {
    if (Math.abs(val) >= 1000000) {
      return (val / 1000000).toFixed(1) + 'M';
    } else if (Math.abs(val) >= 1000) {
      return (val / 1000).toFixed(1) + 'K';
    } else if (Number.isInteger(val)) {
      return val.toString();
    } else {
      return val.toFixed(2);
    }
  };

  // Get trend icon and color
  const getTrendInfo = () => {
    if (!trend) return null;

    switch (trend) {
      case 'up':
        return {
          icon: <TrendingUp fontSize="small" />,
          color: theme.palette.success.main
        };
      case 'down':
        return {
          icon: <TrendingDown fontSize="small" />,
          color: theme.palette.error.main
        };
      case 'flat':
        return {
          icon: <TrendingFlat fontSize="small" />,
          color: theme.palette.text.secondary
        };
      default:
        return null;
    }
  };

  const trendInfo = getTrendInfo();

  return (
    <Box 
      display="flex" 
      flexDirection="column" 
      justifyContent="center" 
      alignItems="center" 
      height="100%"
      p={2}
    >
      {label && (
        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
          {label}
        </Typography>
      )}
      
      <Box display="flex" alignItems="center">
        <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
          {formatValue(value)}
        </Typography>
        
        {trendInfo && (
          <Box ml={1} display="flex" alignItems="center" color={trendInfo.color}>
            {trendInfo.icon}
            {previousValue !== null && (
              <Typography variant="body2" sx={{ ml: 0.5 }}>
                {Math.abs(((value - previousValue) / Math.abs(previousValue)) * 100).toFixed(1)}%
              </Typography>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}; 
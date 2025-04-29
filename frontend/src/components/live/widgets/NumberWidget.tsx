import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

interface NumberWidgetProps {
  data: number | string | Array<number | string | Record<string, number | string>>;
}

export const NumberWidget: React.FC<NumberWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Extract the numeric value from the data
  const value = React.useMemo(() => {
    if (!data || (Array.isArray(data) && data.length === 0)) return null;
    
    // If data is an array, take the first value
    if (Array.isArray(data)) {
      const firstRow = data[0];
      // If the row is an object, take the first numeric value
      if (typeof firstRow === 'object' && !Array.isArray(firstRow)) {
        const firstValue = Object.values(firstRow)[0];
        return typeof firstValue === 'number' ? firstValue : Number(firstValue);
      }
      return typeof firstRow === 'number' ? firstRow : Number(firstRow);
    }
    
    // If data is a single value
    return typeof data === 'number' ? data : Number(data);
  }, [data]);

  if (value === null || isNaN(value)) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  // Format the number with appropriate precision
  const formattedValue = React.useMemo(() => {
    if (Number.isInteger(value)) {
      return value.toLocaleString();
    }
    return value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }, [value]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      height="100%"
      minHeight={200}
    >
      <Typography
        variant="h2"
        component="div"
        sx={{
          color: theme.palette.primary.main,
          fontWeight: 'bold',
          textAlign: 'center'
        }}
      >
        {formattedValue}
      </Typography>
    </Box>
  );
}; 
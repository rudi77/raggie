import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

interface TextWidgetProps {
  data: string | Array<string | Record<string, string>>;
}

export const TextWidget: React.FC<TextWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Extract the text value from the data
  const text = React.useMemo(() => {
    if (!data || (Array.isArray(data) && data.length === 0)) return null;
    
    // If data is an array, take the first value
    if (Array.isArray(data)) {
      const firstRow = data[0];
      // If the row is an object, take the first string value
      if (typeof firstRow === 'object' && !Array.isArray(firstRow)) {
        return String(Object.values(firstRow)[0]);
      }
      return String(firstRow);
    }
    
    // If data is a single value
    return String(data);
  }, [data]);

  if (!text) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      height="100%"
      minHeight={200}
      p={2}
    >
      <Typography
        variant="body1"
        component="div"
        sx={{
          color: theme.palette.text.primary,
          textAlign: 'center',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}
      >
        {text}
      </Typography>
    </Box>
  );
}; 
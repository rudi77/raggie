import React, { useMemo } from 'react';
import { Box, Typography, Paper, useTheme } from '@mui/material';

interface TextWidgetProps {
  data: any;
}

export const TextWidget: React.FC<TextWidgetProps> = ({ data }) => {
  const theme = useTheme();

  // Process data for display
  const textContent = useMemo(() => {
    if (!data) return null;

    // If data is a string, use it directly
    if (typeof data === 'string') {
      return data;
    }

    // If data is an object with text or content property
    if (data.hasOwnProperty('text') || data.hasOwnProperty('content')) {
      return data.text || data.content;
    }

    // If data is an array, join the elements
    if (Array.isArray(data)) {
      return data.map(item => {
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
          return JSON.stringify(item);
        }
        return String(item);
      }).join('\n');
    }

    // If data is an object, stringify it
    if (typeof data === 'object') {
      return JSON.stringify(data, null, 2);
    }

    // Default case: convert to string
    return String(data);
  }, [data]);

  if (!textContent) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No data available
        </Typography>
      </Box>
    );
  }

  // Check if the content is JSON
  const isJson = useMemo(() => {
    try {
      JSON.parse(textContent);
      return true;
    } catch (e) {
      return false;
    }
  }, [textContent]);

  return (
    <Box sx={{ height: '100%', p: 1 }}>
      <Paper 
        variant="outlined" 
        sx={{ 
          height: '100%', 
          p: 2, 
          overflow: 'auto',
          backgroundColor: isJson ? theme.palette.background.default : 'transparent',
          fontFamily: isJson ? 'monospace' : 'inherit'
        }}
      >
        {isJson ? (
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
            {textContent}
          </pre>
        ) : (
          <Typography variant="body2" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
            {textContent}
          </Typography>
        )}
      </Paper>
    </Box>
  );
}; 
import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  useTheme,
  Box,
  alpha
} from '@mui/material';

interface TableWidgetProps {
  data: any[];
}

export const TableWidget: React.FC<TableWidgetProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Typography color="textSecondary" align="center">
        Keine Daten verfügbar
      </Typography>
    );
  }

  // Get column names from the first row
  const columns = Object.keys(data[0]);
  
  // Calculate column width based on available space
  const columnWidth = '150px'; // Fixed column width

  return (
    <Box sx={{
      width: '100%',
      height: '100%',
      maxWidth: '500px', // Match the LineChart width
      margin: '0 auto', // Center the table
    }}>
      <TableContainer 
        component={Paper} 
        sx={{ 
          height: '100%',
          width: '100%',
          backgroundColor: theme.palette.background.paper,
          overflow: 'auto',
          borderRadius: '2px',
          boxShadow: 'none',
          border: `1px solid ${theme.palette.divider}`,
          '& .MuiTableCell-root': {
            borderColor: theme.palette.divider,
            whiteSpace: 'nowrap', // Prevent text wrapping
            padding: '6px 12px', // Reduced padding
            color: theme.palette.text.primary,
            '&:first-of-type': {
              position: 'sticky',
              left: 0,
              backgroundColor: theme.palette.background.paper,
              zIndex: 2,
              borderRight: `1px solid ${theme.palette.divider}`
            }
          },
          '& .MuiTable-root': {
            width: 'max-content', // Allow table to be wider than container
            minWidth: '100%'
          },
          // Custom scrollbar styling
          '&::-webkit-scrollbar': {
            height: '8px',
            width: '8px'
          },
          '&::-webkit-scrollbar-track': {
            background: theme.palette.mode === 'dark' 
              ? theme.palette.grey[800] 
              : theme.palette.grey[200]
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme.palette.mode === 'dark'
              ? theme.palette.grey[600]
              : theme.palette.grey[400],
            borderRadius: '2px',
            '&:hover': {
              background: theme.palette.mode === 'dark'
                ? theme.palette.grey[500]
                : theme.palette.grey[500]
            }
          }
        }}
      >
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell 
                  key={column}
                  sx={{
                    backgroundColor: theme.palette.mode === 'dark'
                      ? alpha(theme.palette.primary.main, 0.2)
                      : alpha(theme.palette.primary.main, 0.1),
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    width: columnWidth,
                    minWidth: columnWidth,
                    maxWidth: columnWidth,
                    fontSize: '0.875rem',
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase',
                    borderBottom: `2px solid ${theme.palette.divider}`,
                    '&:first-of-type': {
                      backgroundColor: theme.palette.mode === 'dark'
                        ? alpha(theme.palette.primary.main, 0.2)
                        : alpha(theme.palette.primary.main, 0.1),
                      zIndex: 3 // Above sticky column cells
                    }
                  }}
                >
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow 
                key={rowIndex}
                sx={{
                  '&:nth-of-type(odd)': {
                    backgroundColor: theme.palette.mode === 'dark'
                      ? alpha(theme.palette.primary.main, 0.05)
                      : alpha(theme.palette.primary.main, 0.02),
                    '& .MuiTableCell-root:first-of-type': {
                      backgroundColor: theme.palette.mode === 'dark'
                        ? alpha(theme.palette.primary.main, 0.05)
                        : alpha(theme.palette.primary.main, 0.02)
                    }
                  },
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark'
                      ? alpha(theme.palette.primary.main, 0.1)
                      : alpha(theme.palette.primary.main, 0.05),
                    '& .MuiTableCell-root:first-of-type': {
                      backgroundColor: theme.palette.mode === 'dark'
                        ? alpha(theme.palette.primary.main, 0.1)
                        : alpha(theme.palette.primary.main, 0.05)
                    }
                  }
                }}
              >
                {columns.map((column) => (
                  <TableCell 
                    key={`${rowIndex}-${column}`}
                    sx={{
                      width: columnWidth,
                      minWidth: columnWidth,
                      maxWidth: columnWidth,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}
                  >
                    {formatCellValue(row[column])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

const formatCellValue = (value: any): string => {
  if (value === null || value === undefined) {
    return '-';
  }

  if (typeof value === 'number') {
    // Format numbers with appropriate precision and locale
    return new Intl.NumberFormat('de-DE', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(value);
  }

  if (typeof value === 'boolean') {
    return value ? 'Ja' : 'Nein';
  }

  if (value instanceof Date) {
    return value.toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Try to parse date strings
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value)) {
    try {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString('de-DE', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    } catch {
      // If parsing fails, return the original string
    }
  }

  return String(value);
}; 
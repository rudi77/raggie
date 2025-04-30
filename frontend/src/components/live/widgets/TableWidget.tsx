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
  Box
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
          '& .MuiTableCell-root': {
            borderColor: theme.palette.divider,
            whiteSpace: 'nowrap', // Prevent text wrapping
            padding: '8px 16px', // Consistent padding
            '&:first-of-type': {
              position: 'sticky',
              left: 0,
              backgroundColor: theme.palette.background.paper,
              zIndex: 2
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
            background: theme.palette.background.default
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme.palette.grey[400],
            borderRadius: '4px',
            '&:hover': {
              background: theme.palette.grey[500]
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
                    backgroundColor: theme.palette.background.default,
                    color: theme.palette.text.primary,
                    fontWeight: 'bold',
                    width: columnWidth,
                    minWidth: columnWidth,
                    maxWidth: columnWidth,
                    '&:first-of-type': {
                      backgroundColor: theme.palette.background.default,
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
                    backgroundColor: theme.palette.action.hover,
                    '& .MuiTableCell-root:first-of-type': {
                      backgroundColor: theme.palette.action.hover
                    }
                  },
                  '&:hover': {
                    backgroundColor: theme.palette.action.selected,
                    '& .MuiTableCell-root:first-of-type': {
                      backgroundColor: theme.palette.action.selected
                    }
                  }
                }}
              >
                {columns.map((column) => (
                  <TableCell 
                    key={`${rowIndex}-${column}`}
                    sx={{
                      color: theme.palette.text.primary,
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
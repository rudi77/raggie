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
  useTheme
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

  return (
    <TableContainer 
      component={Paper} 
      sx={{ 
        maxHeight: 400,
        backgroundColor: theme.palette.background.paper,
        '& .MuiTableCell-root': {
          borderColor: theme.palette.divider
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
                  fontWeight: 'bold'
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
                  backgroundColor: theme.palette.action.hover
                },
                '&:hover': {
                  backgroundColor: theme.palette.action.selected
                }
              }}
            >
              {columns.map((column) => (
                <TableCell 
                  key={`${rowIndex}-${column}`}
                  sx={{
                    color: theme.palette.text.primary
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
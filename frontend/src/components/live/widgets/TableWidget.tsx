import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography
} from '@mui/material';

interface TableWidgetProps {
  data: any[];
}

export const TableWidget: React.FC<TableWidgetProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <Typography color="textSecondary" align="center">
        No data available
      </Typography>
    );
  }

  // Get column names from the first row
  const columns = Object.keys(data[0]);

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column}>{column}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <TableRow key={index}>
              {columns.map((column) => (
                <TableCell key={`${index}-${column}`}>
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
    // Format numbers with appropriate precision
    return Number.isInteger(value) ? value.toString() : value.toFixed(2);
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  if (value instanceof Date) {
    return value.toLocaleString();
  }

  return String(value);
}; 
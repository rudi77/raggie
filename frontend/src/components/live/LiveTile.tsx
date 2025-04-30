import React from 'react';
import { SQLTemplate, WidgetType } from '../../services/template.service';
import {
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Typography,
  Box,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { TableWidget } from './widgets/TableWidget';
import { LineChartWidget } from './widgets/LineChartWidget';
import { BarChartWidget } from './widgets/BarChartWidget';
import { PieChartWidget } from './widgets/PieChartWidget';
import { NumberWidget } from './widgets/NumberWidget';
import { TextWidget } from './widgets/TextWidget';

interface LiveTileProps {
  template: SQLTemplate;
  data: any;
  error?: string;
  lastUpdate: string;
}

const getWidgetComponent = (widgetType: WidgetType, data: any) => {
  switch (widgetType) {
    case WidgetType.TABLE:
      return <TableWidget data={data} />;
    case WidgetType.LINE_CHART:
      return <LineChartWidget data={data} />;
    case WidgetType.BAR_CHART:
      return <BarChartWidget data={data} />;
    case WidgetType.PIE_CHART:
      return <PieChartWidget data={data} />;
    case WidgetType.NUMBER:
      return <NumberWidget data={data} />;
    case WidgetType.TEXT:
      return <TextWidget data={data} />;
    default:
      return (
        <Typography color="error">
          Unsupported widget type: {widgetType}
        </Typography>
      );
  }
};

export const LiveTile: React.FC<LiveTileProps> = ({
  template,
  data,
  error,
  lastUpdate
}) => {
  const handleRefresh = () => {
    // TODO: Implement manual refresh
    console.log('Manual refresh requested for template:', template.id);
  };

  return (
    <Card sx={{ 
      height: '400px', // Fixed height for all tiles
      width: '100%', // Take full width of grid item
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden', // Prevent content from expanding the card
      minWidth: '500px' // Minimum width based on LineChart
    }}>
      <CardHeader
        sx={{
          p: 2, // Consistent padding
          '& .MuiCardHeader-content': {
            overflow: 'hidden', // Prevent title from expanding
            minWidth: 0 // Allow text to truncate
          },
          '& .MuiCardHeader-title': {
            fontSize: '1rem',
            fontWeight: 500,
            lineHeight: 1.2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            height: '2.4em' // Fixed height for 2 lines
          }
        }}
        title={template.source_question}
        action={
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }
        subheader={
          <Typography variant="caption" color="textSecondary">
            Updated {formatDistanceToNow(new Date(lastUpdate))} ago
          </Typography>
        }
      />
      <CardContent sx={{ 
        flexGrow: 1, 
        position: 'relative',
        height: 'calc(100% - 85px)', // Subtract header height
        p: 2, // Consistent padding
        overflow: 'hidden' // Hide overflow at container level
      }}>
        {error ? (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        ) : data === null ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="100%"
          >
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ 
            height: '100%',
            width: '100%',
            overflow: 'auto', // Enable both scrollbars
            '& > *': { // Apply to all widget components
              height: '100%',
              width: '100%',
              minWidth: '500px', // Consistent minimum width for all widgets
            },
            // Custom scrollbar styling
            '&::-webkit-scrollbar': {
              width: '8px',
              height: '8px'
            },
            '&::-webkit-scrollbar-track': {
              background: '#f1f1f1'
            },
            '&::-webkit-scrollbar-thumb': {
              background: '#888',
              borderRadius: '4px',
              '&:hover': {
                background: '#666'
              }
            }
          }}>
            {getWidgetComponent(template.widget_type, data)}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}; 
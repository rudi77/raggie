import React, { useEffect, useState } from 'react';
import { templateService, SQLTemplate } from '../../services/template.service';
import { websocketService, LiveUpdate } from '../../services/websocket.service';
import { LiveTile } from './LiveTile';
import { Alert, AlertTitle, Box, CircularProgress, Grid, Typography } from '@mui/material';

interface TileData {
  template: SQLTemplate;
  data: any;
  error?: string;
  lastUpdate: string;
}

export const LiveTileGrid: React.FC = () => {
  const [tiles, setTiles] = useState<Map<number, TileData>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load templates and connect to WebSocket
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        await templateService.fetchTemplates();
        const templates = templateService.getAllTemplates();
        
        // Initialize tiles with templates
        const initialTiles = new Map<number, TileData>();
        templates.forEach(template => {
          initialTiles.set(template.id, {
            template,
            data: null,
            lastUpdate: template.last_execution || new Date().toISOString()
          });
        });
        
        setTiles(initialTiles);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load templates');
        setIsLoading(false);
      }
    };

    loadTemplates();
    websocketService.connect();

    // Cleanup - properly disconnect when component unmounts
    return () => {
      websocketService.disconnect();
    };
  }, []);

  // Handle live updates
  useEffect(() => {
    const handleLiveUpdate = (update: LiveUpdate) => {
      if (!update || !update.template_id) {
        console.warn('Received invalid live update:', update);
        return;
      }

      setTiles(prevTiles => {
        const newTiles = new Map(prevTiles);
        const tile = newTiles.get(update.template_id);
        
        if (tile) {
          newTiles.set(update.template_id, {
            ...tile,
            data: update.data?.result || null,
            error: update.error,
            lastUpdate: update.timestamp || new Date().toISOString()
          });
        } else {
          console.warn(`Received update for unknown template ID: ${update.template_id}`);
        }
        
        return newTiles;
      });
    };

    websocketService.onLiveUpdate(handleLiveUpdate);

    return () => {
      websocketService.offLiveUpdate(handleLiveUpdate);
    };
  }, []);

  // Handle template updates
  useEffect(() => {
    const handleTemplatesUpdated = (templates: SQLTemplate[]) => {
      setTiles(prevTiles => {
        const newTiles = new Map(prevTiles);
        
        templates.forEach(template => {
          if (!newTiles.has(template.id)) {
            newTiles.set(template.id, {
              template,
              data: null,
              lastUpdate: template.last_execution || new Date().toISOString()
            });
          }
        });
        
        return newTiles;
      });
    };

    const handleTemplateDeleted = (id: number) => {
      setTiles(prevTiles => {
        const newTiles = new Map(prevTiles);
        newTiles.delete(id);
        return newTiles;
      });
    };

    templateService.onTemplatesUpdated(handleTemplatesUpdated);
    templateService.onTemplateDeleted(handleTemplateDeleted);

    return () => {
      templateService.offTemplatesUpdated(handleTemplatesUpdated);
      templateService.offTemplateDeleted(handleTemplateDeleted);
    };
  }, []);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        <AlertTitle>Error</AlertTitle>
        {error}
      </Alert>
    );
  }

  if (tiles.size === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography variant="h6" color="textSecondary">
          No live tiles available. Create a template to get started.
        </Typography>
      </Box>
    );
  }

  return (
    <Grid 
      container 
      spacing={3} 
      sx={{ 
        p: 3,
        width: '100%',
        margin: 0,
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(500px, 1fr))',
        gap: '24px',
        '& .MuiGrid-item': {
          padding: 0,
          width: '100%',
          maxWidth: '100%',
          flexBasis: '100%'
        }
      }}
    >
      {Array.from(tiles.values()).map(({ template, data, error, lastUpdate }) => (
        <div
          key={template.id}
          style={{ display: 'flex', width: '100%' }}
        >
          <LiveTile
            template={template}
            data={data}
            error={error}
            lastUpdate={lastUpdate}
          />
        </div>
      ))}
    </Grid>
  );
}; 
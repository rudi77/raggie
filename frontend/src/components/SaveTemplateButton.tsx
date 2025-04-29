import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack
} from '@mui/material';
import { WidgetType } from '../services/template.service';
import { templateService } from '../services/template.service';
import SaveIcon from '@mui/icons-material/Save';

interface SaveTemplateButtonProps {
  query: string;
  sourceQuestion: string;
}

export const SaveTemplateButton: React.FC<SaveTemplateButtonProps> = ({ query, sourceQuestion }) => {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [widgetType, setWidgetType] = useState<WidgetType>(WidgetType.TABLE);
  const [refreshRate, setRefreshRate] = useState(0);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSave = async () => {
    try {
      await templateService.createTemplate({
        name,
        description,
        query,
        source_question: sourceQuestion,
        widget_type: widgetType,
        refresh_rate: refreshRate
      });
      handleClose();
    } catch (error) {
      console.error('Error saving template:', error);
      // TODO: Add error handling/notification
    }
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<SaveIcon />}
        onClick={handleOpen}
        size="small"
      >
        Als Template speichern
      </Button>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Template speichern</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              required
            />
            <TextField
              label="Beschreibung"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              rows={2}
            />
            <FormControl fullWidth>
              <InputLabel>Widget Typ</InputLabel>
              <Select
                value={widgetType}
                label="Widget Typ"
                onChange={(e) => setWidgetType(e.target.value as WidgetType)}
              >
                <MenuItem value={WidgetType.TABLE}>Tabelle</MenuItem>
                <MenuItem value={WidgetType.LINE_CHART}>Liniendiagramm</MenuItem>
                <MenuItem value={WidgetType.BAR_CHART}>Balkendiagramm</MenuItem>
                <MenuItem value={WidgetType.PIE_CHART}>Kreisdiagramm</MenuItem>
                <MenuItem value={WidgetType.NUMBER}>Zahl</MenuItem>
                <MenuItem value={WidgetType.TEXT}>Text</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Aktualisierungsintervall (Sekunden)"
              type="number"
              value={refreshRate}
              onChange={(e) => setRefreshRate(parseInt(e.target.value) || 0)}
              fullWidth
              InputProps={{ inputProps: { min: 0 } }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Abbrechen</Button>
          <Button onClick={handleSave} variant="contained" disabled={!name}>
            Speichern
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 
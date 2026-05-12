'use client';

import React, { useState } from 'react';
import { 
  Box, Typography, Button, Paper, Stepper, Step, StepLabel, 
  TextField, Slider, Grid, IconButton, List, ListItem, 
  ListItemText, ListItemSecondaryAction 
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { submitOnboarding } from '../lib/api';

const steps = ['Basic Info', 'Academic Details', 'Learning Style', 'Mental Health'];

const Onboarding = ({ onComplete }: { onComplete: () => void }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    age: 20,
    current_education_degree: '',
    current_education_major: '',
    current_education_year: 1,
    current_grades: [] as any[],
    subjects: [] as string[],
    exams_preparing_for: [] as any[],
    academic_strengths: [] as string[],
    academic_weaknesses: [] as string[],
    learning_style: {
      preferred_study_times: '',
      strengths: [] as string[],
      weaknesses: [] as string[]
    },
    education_goals: '',
    stress_level: 0.5,
    burnout_history: ''
  });

  const [newItem, setNewItem] = useState('');
  const [newItemStrength, setNewItemStrength] = useState('');
  const [newItemWeakness, setNewItemWeakness] = useState('');

  const handleNext = async () => {
    if (activeStep === steps.length - 1) {
      await submitOnboarding(formData);
      onComplete();
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => setActiveStep((prev) => prev - 1);

  const addItem = (field: string, value: any) => {
    if (!value) return;
    setFormData((prev: any) => ({
      ...prev,
      [field]: [...prev[field], value]
    }));
    if (field === 'subjects') setNewItem('');
    if (field === 'academic_strengths') setNewItemStrength('');
    if (field === 'academic_weaknesses') setNewItemWeakness('');
  };

  const removeItem = (field: string, index: number) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: prev[field].filter((_: any, i: number) => i !== index)
    }));
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Age" type="number" fullWidth 
                value={formData.age} 
                onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Degree" fullWidth 
                value={formData.current_education_degree}
                onChange={(e) => setFormData({...formData, current_education_degree: e.target.value})}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Major" fullWidth 
                value={formData.current_education_major}
                onChange={(e) => setFormData({...formData, current_education_major: e.target.value})}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Current Year" type="number" fullWidth 
                value={formData.current_education_year}
                onChange={(e) => setFormData({...formData, current_education_year: parseInt(e.target.value)})}
              />
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Academic Context</Typography>
            
            <Typography variant="subtitle2" sx={{ mt: 2 }}>Subjects</Typography>
            <Box sx={{ display: 'flex', mb: 1 }}>
              <TextField 
                size="small" fullWidth value={newItem} 
                onChange={(e) => setNewItem(e.target.value)} 
                placeholder="e.g. Mathematics"
              />
              <IconButton onClick={() => addItem('subjects', newItem)}><AddIcon /></IconButton>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {formData.subjects.map((s, i) => (
                    <Paper key={i} variant="outlined" sx={{ px: 1, py: 0.5, display: 'flex', alignItems: 'center' }}>
                        <Typography variant="caption">{s}</Typography>
                        <IconButton size="small" onClick={() => removeItem('subjects', i)}><DeleteIcon sx={{ fontSize: 16 }} /></IconButton>
                    </Paper>
                ))}
            </Box>

            <Typography variant="subtitle2">Strengths</Typography>
            <Box sx={{ display: 'flex', mb: 1 }}>
              <TextField 
                size="small" fullWidth value={newItemStrength} 
                onChange={(e) => setNewItemStrength(e.target.value)} 
                placeholder="e.g. Critical Thinking"
              />
              <IconButton onClick={() => addItem('academic_strengths', newItemStrength)}><AddIcon /></IconButton>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {formData.academic_strengths.map((s, i) => (
                    <Paper key={i} variant="outlined" sx={{ px: 1, py: 0.5, display: 'flex', alignItems: 'center', borderColor: 'success.light' }}>
                        <Typography variant="caption">{s}</Typography>
                        <IconButton size="small" onClick={() => removeItem('academic_strengths', i)}><DeleteIcon sx={{ fontSize: 16 }} /></IconButton>
                    </Paper>
                ))}
            </Box>

            <Typography variant="subtitle2">Weaknesses</Typography>
            <Box sx={{ display: 'flex', mb: 1 }}>
              <TextField 
                size="small" fullWidth value={newItemWeakness} 
                onChange={(e) => setNewItemWeakness(e.target.value)} 
                placeholder="e.g. Time Management"
              />
              <IconButton onClick={() => addItem('academic_weaknesses', newItemWeakness)}><AddIcon /></IconButton>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {formData.academic_weaknesses.map((s, i) => (
                    <Paper key={i} variant="outlined" sx={{ px: 1, py: 0.5, display: 'flex', alignItems: 'center', borderColor: 'error.light' }}>
                        <Typography variant="caption">{s}</Typography>
                        <IconButton size="small" onClick={() => removeItem('academic_weaknesses', i)}><DeleteIcon sx={{ fontSize: 16 }} /></IconButton>
                    </Paper>
                ))}
            </Box>
          </Box>
        );
      case 2:
        return (
          <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Education Goals" multiline rows={3} fullWidth 
                value={formData.education_goals}
                onChange={(e) => setFormData({...formData, education_goals: e.target.value})}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField 
                label="Preferred Study Times" fullWidth 
                value={formData.learning_style.preferred_study_times}
                onChange={(e) => setFormData({
                  ...formData, 
                  learning_style: {...formData.learning_style, preferred_study_times: e.target.value}
                })}
              />
            </Grid>
          </Grid>
        );
      case 3:
        return (
          <Box>
            <Typography gutterBottom>Stress Level (0-1)</Typography>
            <Slider 
              value={formData.stress_level} min={0} max={1} step={0.1} 
              onChange={(_, v) => setFormData({...formData, stress_level: v as number})}
              valueLabelDisplay="auto"
            />
            <TextField 
              label="Burnout History" multiline rows={3} fullWidth sx={{ mt: 2 }}
              value={formData.burnout_history}
              onChange={(e) => setFormData({...formData, burnout_history: e.target.value})}
            />
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}><StepLabel>{label}</StepLabel></Step>
        ))}
      </Stepper>
      <Paper elevation={3} sx={{ p: 4, minHeight: 300 }}>
        {renderStepContent(activeStep)}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
          {activeStep !== 0 && (
            <Button onClick={handleBack} sx={{ mr: 1 }}>Back</Button>
          )}
          <Button variant="contained" onClick={handleNext}>
            {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Onboarding;

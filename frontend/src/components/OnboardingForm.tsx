'use client';

import React, { useState } from 'react';

interface OnboardingFormProps {
  onComplete: (data: any) => void;
}

export default function OnboardingForm({ onComplete }: OnboardingFormProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    age: 20,
    current_education: { degree: '', major: '', year: 1 },
    past_education: [],
    current_grades: {},
    subjects: '',
    exams_preparing_for: '',
    academic_strengths: '',
    academic_weaknesses: '',
    learning_style: { preferred_study_times: 'morning' },
    education_goals: '',
    baseline_mental_health: { stress_level: 0.5, burnout_history: 'none' }
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: { ...(prev as any)[parent], [child]: value }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Process string inputs into lists for the backend
    const processedData = {
      ...formData,
      subjects: formData.subjects.split(',').map(s => s.trim()),
      academic_strengths: formData.academic_strengths.split(',').map(s => s.trim()),
      academic_weaknesses: formData.academic_weaknesses.split(',').map(s => s.trim()),
      exams_preparing_for: formData.exams_preparing_for.split(',').map(s => ({ name: s.trim() }))
    };
    onComplete(processedData);
  };

  return (
    <div className="card">
      <h2 className="title">Welcome to Student Buddy</h2>
      <p className="subtitle">Step {step} of 4: Let's get to know you</p>

      <form onSubmit={handleSubmit}>
        {step === 1 && (
          <div className="step-content">
            <div className="form-group">
              <label>Age</label>
              <input type="number" name="age" value={formData.age} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Current Degree</label>
              <input type="text" name="current_education.degree" value={formData.current_education.degree} onChange={handleChange} placeholder="e.g. B.Sc" />
            </div>
            <div className="form-group">
              <label>Major</label>
              <input type="text" name="current_education.major" value={formData.current_education.major} onChange={handleChange} placeholder="e.g. Computer Science" />
            </div>
            <button type="button" className="btn-primary" onClick={nextStep}>Next</button>
          </div>
        )}

        {step === 2 && (
          <div className="step-content">
            <div className="form-group">
              <label>Current Subjects (comma separated)</label>
              <textarea name="subjects" value={formData.subjects} onChange={handleChange} placeholder="Physics, Calculus, History..." />
            </div>
            <div className="form-group">
              <label>Exams you're preparing for</label>
              <input type="text" name="exams_preparing_for" value={formData.exams_preparing_for} onChange={handleChange} placeholder="Midterms, GRE, finals..." />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="button" style={{ background: '#ccc' }} onClick={prevStep}>Back</button>
              <button type="button" className="btn-primary" onClick={nextStep}>Next</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="step-content">
            <div className="form-group">
              <label>Academic Strengths</label>
              <input type="text" name="academic_strengths" value={formData.academic_strengths} onChange={handleChange} placeholder="Mathematics, Writing..." />
            </div>
            <div className="form-group">
              <label>Academic Weaknesses</label>
              <input type="text" name="academic_weaknesses" value={formData.academic_weaknesses} onChange={handleChange} placeholder="Time management, Memorization..." />
            </div>
            <div className="form-group">
              <label>Long-term Education Goals</label>
              <textarea name="education_goals" value={formData.education_goals} onChange={handleChange} placeholder="I want to become a researcher in AI..." />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="button" style={{ background: '#ccc' }} onClick={prevStep}>Back</button>
              <button type="button" className="btn-primary" onClick={nextStep}>Next</button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="step-content">
            <div className="form-group">
              <label>Preferred Study Time</label>
              <select name="learning_style.preferred_study_times" value={formData.learning_style.preferred_study_times} onChange={handleChange}>
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
                <option value="night">Night</option>
              </select>
            </div>
            <div className="form-group">
              <label>Current Stress Level (0-1)</label>
              <input type="range" min="0" max="1" step="0.1" name="baseline_mental_health.stress_level" value={formData.baseline_mental_health.stress_level} onChange={handleChange} />
              <div style={{ textAlign: 'center' }}>{formData.baseline_mental_health.stress_level}</div>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="button" style={{ background: '#ccc' }} onClick={prevStep}>Back</button>
              <button type="submit" className="btn-primary">Complete Onboarding</button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

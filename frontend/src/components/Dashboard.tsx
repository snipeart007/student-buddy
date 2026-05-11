'use client';

import React from 'react';

interface DashboardProps {
  studentState: any;
}

export default function Dashboard({ studentState }: DashboardProps) {
  if (!studentState) return null;

  const { academic, mental_health } = studentState;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
      <div className="card">
        <h3>Academic Standing</h3>
        <p><strong>Education:</strong> {academic.current_education}</p>
        <p><strong>GPA Trend:</strong> {academic.gpa_trend > 0 ? '+' : ''}{academic.gpa_trend}</p>
        <p><strong>Backlog:</strong> {academic.assignment_backlog} items</p>
      </div>
      
      <div className="card">
        <h3>Mental Wellbeing</h3>
        <div className="stat-row">
          <label>Stress:</label>
          <div className="progress-bar">
            <div className="progress" style={{ width: `${mental_health.stress_level * 100}%`, background: 'var(--error)' }}></div>
          </div>
        </div>
        <div className="stat-row">
          <label>Burnout:</label>
          <div className="progress-bar">
            <div className="progress" style={{ width: `${mental_health.burnout_level * 100}%`, background: 'orange' }}></div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .stat-row {
          margin-top: 10px;
        }
        .progress-bar {
          width: 100%;
          height: 10px;
          background: #e9ecef;
          border-radius: 5px;
          overflow: hidden;
          margin-top: 5px;
        }
        .progress {
          height: 100%;
          transition: width 0.3s ease;
        }
        h3 {
          margin-bottom: 15px;
          border-bottom: 2px solid var(--background);
          padding-bottom: 5px;
        }
      `}</style>
    </div>
  );
}

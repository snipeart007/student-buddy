'use client';

import React, { useState } from 'react';
import OnboardingForm from '@/components/OnboardingForm';
import ChatInterface from '@/components/ChatInterface';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [userId, setUserId] = useState<string | null>(null);
  const [isOnboarding, setIsOnboarding] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [studentState, setStudentState] = useState<any>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      setUserId(data.user_id);
      setIsOnboarding(true);
    } catch (err) {
      alert('Registration failed');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (res.ok) {
        const data = await res.json();
        setUserId(data.user_id);
        setIsLoggedIn(true);
      } else {
        alert('Login failed');
      }
    } catch (err) {
      alert('Login error');
    }
  };

  const handleOnboardingComplete = async (onboardingData: any) => {
    try {
      const res = await fetch(`http://localhost:8000/onboarding/submit?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(onboardingData),
      });
      const data = await res.json();
      setStudentState(data.initial_state);
      setIsOnboarding(false);
      setIsLoggedIn(true);
    } catch (err) {
      alert('Onboarding submission failed');
    }
  };

  if (!userId && !isLoggedIn) {
    return (
      <div className="container">
        <div className="card">
          <h1 className="title">Student Buddy</h1>
          <p className="subtitle">Your AI-powered academic and wellness advisor</p>
          
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Username</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" className="btn-primary">Login</button>
              <button type="button" onClick={handleRegister} style={{ background: 'var(--accent)', color: 'white', width: '100%' }}>Register</button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  if (isOnboarding) {
    return (
      <div className="container">
        <OnboardingForm onComplete={handleOnboardingComplete} />
      </div>
    );
  }

  return (
    <div className="container">
      <h1 className="title">Student Buddy</h1>
      <p className="subtitle">Signed in as {username}</p>
      <Dashboard studentState={studentState} />
      <ChatInterface userId={userId!} onResponse={(data) => setStudentState(data.updated_state)} />
    </div>
  );
}

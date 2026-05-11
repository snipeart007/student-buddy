'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  action_items?: string[];
  follow_up_questions?: string[];
}

interface ChatInterfaceProps {
  userId: string;
  onResponse?: (data: any) => void;
}

export default function ChatInterface({ userId, onResponse }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, query: input }),
      });

      const data = await response.json();
      if (onResponse) onResponse(data);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        action_items: data.action_items,
        follow_up_questions: data.follow_up_questions,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
      <div className="messages" style={{ flex: 1, overflowY: 'auto', marginBottom: '20px', padding: '10px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ 
            marginBottom: '15px', 
            textAlign: msg.role === 'user' ? 'right' : 'left',
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{ 
              display: 'inline-block', 
              padding: '10px 15px', 
              borderRadius: '15px', 
              background: msg.role === 'user' ? 'var(--primary)' : '#e9ecef',
              color: msg.role === 'user' ? 'white' : 'var(--foreground)',
              maxWidth: '80%'
            }}>
              {msg.content}
            </div>
            
            {msg.action_items && msg.action_items.length > 0 && (
              <div style={{ fontSize: '0.85rem', marginTop: '5px', textAlign: 'left', color: 'var(--accent)' }}>
                <strong>Actions:</strong>
                <ul style={{ paddingLeft: '20px' }}>
                  {msg.action_items.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div style={{ color: 'var(--secondary)' }}>Student Buddy is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px' }}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Type your message..." 
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn-primary" style={{ width: 'auto' }}>Send</button>
      </form>
    </div>
  );
}

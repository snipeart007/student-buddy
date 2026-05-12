'use client';

import React from 'react';
import { Box, Paper } from '@mui/material';

const Chat = () => {
  return (
    <Box sx={{ 
      flexGrow: 1,
      width: '100%',
      height: '100%',
      overflow: 'hidden'
    }}>
      <iframe
        src="/advisor_chat/"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          display: 'block'
        }}
        title="Gradio Chat Interface"
        scrolling="no"
      />
    </Box>
  );
};

export default Chat;

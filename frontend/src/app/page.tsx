'use client';

import React, { useState } from 'react';
import Onboarding from "@/components/Onboarding";
import Chat from "@/components/Chat";
import { Box, Container } from "@mui/material";

export default function Home() {
  const [isOnboarded, setIsOnboarded] = useState(false);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {!isOnboarded ? (
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Onboarding onComplete={() => setIsOnboarded(true)} />
        </Container>
      ) : (
        <Chat />
      )}
    </Box>
  );
}

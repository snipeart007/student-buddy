'use client';

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import Link from 'next/link';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Student Buddy
        </Typography>
        <Box>
          <Button color="inherit" component={Link} href="/">
            Home
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

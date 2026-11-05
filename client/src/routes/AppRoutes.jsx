import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Home } from '../pages/Home';
import { ResearchWorkspace } from '../pages/ResearchWorkspace';

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/research/:projectId" element={<ResearchWorkspace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};


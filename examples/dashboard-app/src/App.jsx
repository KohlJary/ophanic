import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import CostAnalysis from './pages/CostAnalysis';
import Scheduling from './pages/Scheduling';
import HallManagement from './pages/HallManagement';
import PricingStrategy from './pages/PricingStrategy';

/**
 * Dashboard App - Generated from Figma via Ophanic
 *
 * Source: Dashboard Design Template (Community)
 * Tokens extracted: 35 colors, 38 typography styles
 */
function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'cost-analysis':
        return <CostAnalysis />;
      case 'scheduling':
        return <Scheduling />;
      case 'hall':
        return <HallManagement />;
      case 'pricing':
        return <PricingStrategy />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--color-color-6)' }}>
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main style={{ flex: 1, overflow: 'auto' }}>
        {renderPage()}
      </main>
    </div>
  );
}

export default App;

import React from 'react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'scheduling', label: 'Screen Scheduling', icon: '📅' },
  { id: 'hall', label: 'Hall Management', icon: '🏛️' },
  { id: 'pricing', label: 'Pricing Strategy', icon: '💰' },
  { id: 'cost-analysis', label: 'Cost Analysis', icon: '📈' },
];

export default function Sidebar({ currentPage, onNavigate }) {
  return (
    <aside
      style={{
        width: '260px',
        background: 'white',
        borderRight: '1px solid var(--color-gray-18)',
        padding: '24px 16px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Logo/Brand */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '32px',
          padding: '0 8px',
        }}
      >
        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'var(--color-blue-1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          D
        </div>
        <div>
          <div
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
            }}
          >
            Dashboard
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-color-10)' }}>
            Cinema Manager
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1 }}>
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                marginBottom: '4px',
                border: 'none',
                borderRadius: '10px',
                background: isActive ? 'var(--color-color-12)' : 'transparent',
                color: isActive ? 'var(--color-blue-1)' : 'var(--color-color-10)',
                fontSize: '14px',
                fontWeight: isActive ? 500 : 400,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ fontSize: '18px' }}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* User Section */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid var(--color-gray-18)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'var(--color-blue-1)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          R
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--color-blue-11)' }}>
            Ravi
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-color-10)' }}>
            Admin
          </div>
        </div>
      </div>
    </aside>
  );
}

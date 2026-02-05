import React, { useState } from 'react';

const screens = [
  { id: 1, name: 'Screen 1', movie: 'Gadar 2' },
  { id: 2, name: 'Screen 2', movie: 'Jawan' },
  { id: 3, name: 'Screen 3', movie: 'Talk To Me (Hindi)' },
  { id: 4, name: 'Screen 4', movie: 'Dream Girl 2' },
];

const timeSlots = [
  '9:00 AM',
  '12:00 PM',
  '3:00 PM',
  '6:00 PM',
  '9:00 PM',
];

const schedule = {
  1: ['Gadar 2', 'Gadar 2', 'Gadar 2', 'Gadar 2', 'Gadar 2'],
  2: ['Jawan', 'Jawan', 'Jawan', 'Jawan', 'Jawan'],
  3: ['Talk To Me', 'Talk To Me', 'Talk To Me', 'Talk To Me', '—'],
  4: ['Dream Girl 2', 'Dream Girl 2', 'Dream Girl 2', 'Dream Girl 2', 'Dream Girl 2'],
};

export default function Scheduling() {
  const [selectedDate, setSelectedDate] = useState('2023-09-15');

  return (
    <div style={{ padding: '24px', maxWidth: '1400px' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
        }}
      >
        <div>
          <h1
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '24px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
              margin: 0,
            }}
          >
            Screen Scheduling
          </h1>
          <p style={{ color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            Manage show timings across all screens
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{
              padding: '10px 16px',
              border: '1px solid var(--color-gray-18)',
              borderRadius: '8px',
              fontSize: '14px',
            }}
          />
          <button
            style={{
              padding: '10px 20px',
              background: 'var(--color-blue-1)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            + Add Show
          </button>
        </div>
      </div>

      {/* Schedule Table */}
      <div style={{ background: 'white', borderRadius: '16px', padding: '24px', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
          <thead>
            <tr>
              <th
                style={{
                  textAlign: 'left',
                  padding: '16px',
                  background: 'var(--color-color-6)',
                  borderRadius: '8px 0 0 8px',
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--color-blue-11)',
                }}
              >
                Screen
              </th>
              {timeSlots.map((slot) => (
                <th
                  key={slot}
                  style={{
                    textAlign: 'center',
                    padding: '16px',
                    background: 'var(--color-color-6)',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: 'var(--color-blue-11)',
                  }}
                >
                  {slot}
                </th>
              ))}
              <th
                style={{
                  textAlign: 'center',
                  padding: '16px',
                  background: 'var(--color-color-6)',
                  borderRadius: '0 8px 8px 0',
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--color-blue-11)',
                }}
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {screens.map((screen) => (
              <tr key={screen.id}>
                <td
                  style={{
                    padding: '16px',
                    borderBottom: '1px solid var(--color-color-6)',
                  }}
                >
                  <div style={{ fontWeight: 500, color: 'var(--color-blue-11)' }}>
                    {screen.name}
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--color-color-10)', marginTop: '2px' }}>
                    {screen.movie}
                  </div>
                </td>
                {schedule[screen.id].map((show, i) => (
                  <td
                    key={i}
                    style={{
                      padding: '12px',
                      borderBottom: '1px solid var(--color-color-6)',
                      textAlign: 'center',
                    }}
                  >
                    {show !== '—' ? (
                      <div
                        style={{
                          padding: '8px 12px',
                          background: 'var(--color-color-12)',
                          borderRadius: '8px',
                          fontSize: '13px',
                          color: 'var(--color-blue-1)',
                          fontWeight: 500,
                        }}
                      >
                        {show}
                      </div>
                    ) : (
                      <div style={{ color: 'var(--color-gray-9)', fontSize: '13px' }}>—</div>
                    )}
                  </td>
                ))}
                <td
                  style={{
                    padding: '12px',
                    borderBottom: '1px solid var(--color-color-6)',
                    textAlign: 'center',
                  }}
                >
                  <button
                    style={{
                      padding: '6px 12px',
                      background: 'transparent',
                      border: '1px solid var(--color-blue-1)',
                      color: 'var(--color-blue-1)',
                      borderRadius: '6px',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '20px' }}>
        {[
          { label: 'Total Shows Today', value: '19' },
          { label: 'Peak Hour', value: '6:00 PM' },
          { label: 'Available Slots', value: '1' },
          { label: 'Expected Footfall', value: '2,400' },
        ].map((stat, i) => (
          <div
            key={i}
            style={{
              background: 'white',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '13px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
              {stat.label}
            </div>
            <div
              style={{
                fontFamily: 'Poppins, sans-serif',
                fontSize: '24px',
                fontWeight: 600,
                color: 'var(--color-blue-11)',
              }}
            >
              {stat.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

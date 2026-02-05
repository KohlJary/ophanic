import React, { useState } from 'react';

const shows = [
  { id: 1, time: '7:00 am - 10:00 am', label: 'Show 1' },
  { id: 2, time: '12:00 pm - 3:00 pm', label: 'Show 2' },
  { id: 3, time: '5:00 pm - 8:00 pm', label: 'Show 3' },
  { id: 4, time: '8:00 pm - 10:30 pm', label: 'Show 4' },
];

const screens = [
  { id: 1, name: 'Screen 1', movie: 'Gadar 2', basePrice: 280 },
  { id: 2, name: 'Screen 2', movie: 'Jawan', basePrice: 320 },
  { id: 3, name: 'Screen 3', movie: 'Talk To Me (Hindi)', basePrice: 250 },
  { id: 4, name: 'Screen 4', movie: 'Dream Girl 2', basePrice: 220 },
];

const days = ['Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu'];

export default function PricingStrategy() {
  const [selectedDay, setSelectedDay] = useState('Fri');
  const [selectedScreen, setSelectedScreen] = useState(screens[0]);

  // Weekend multiplier
  const isWeekend = ['Fri', 'Sat', 'Sun'].includes(selectedDay);
  const multiplier = isWeekend ? 1.2 : 1.0;

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
            Pricing Strategy
          </h1>
          <p style={{ color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            Configure ticket prices by show and day
          </p>
        </div>

        <button
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 20px',
            background: 'var(--color-blue-1)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          Auto set Price
        </button>
      </div>

      {/* Day Selector */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '24px',
          background: 'white',
          padding: '8px',
          borderRadius: '12px',
          width: 'fit-content',
        }}
      >
        {days.map((day) => (
          <button
            key={day}
            onClick={() => setSelectedDay(day)}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              background: selectedDay === day ? 'var(--color-blue-1)' : 'transparent',
              color: selectedDay === day ? 'white' : 'var(--color-color-10)',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {day}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '20px' }}>
        {/* Screen List */}
        <div
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '20px',
          }}
        >
          <h3
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
              marginBottom: '16px',
            }}
          >
            Screens
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {screens.map((screen) => (
              <button
                key={screen.id}
                onClick={() => setSelectedScreen(screen)}
                style={{
                  padding: '14px 16px',
                  border: 'none',
                  borderRadius: '10px',
                  background:
                    selectedScreen.id === screen.id
                      ? 'var(--color-color-12)'
                      : 'var(--color-color-6)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color: 'var(--color-blue-11)',
                  }}
                >
                  {screen.name}
                </div>
                <div
                  style={{
                    fontSize: '12px',
                    color: 'var(--color-color-10)',
                    marginTop: '2px',
                  }}
                >
                  {screen.movie}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Pricing Grid */}
        <div
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px',
            }}
          >
            <div>
              <h3
                style={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: 'var(--color-blue-11)',
                  margin: 0,
                }}
              >
                {selectedScreen.name} - {selectedScreen.movie}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--color-color-10)', margin: '4px 0 0' }}>
                Base price: ₹{selectedScreen.basePrice} • {isWeekend ? 'Weekend (+20%)' : 'Weekday'}
              </p>
            </div>
            <div
              style={{
                background: 'var(--color-color-6)',
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                color: 'var(--color-color-10)',
              }}
            >
              12 notifications
            </div>
          </div>

          {/* Show Times Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            {shows.map((show) => {
              const price = Math.round(selectedScreen.basePrice * multiplier);
              // Premium for evening shows
              const showPrice = show.id >= 3 ? price + 50 : price;

              return (
                <div
                  key={show.id}
                  style={{
                    background: 'var(--color-color-6)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                  }}
                >
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: 500,
                      color: 'var(--color-blue-11)',
                      marginBottom: '4px',
                    }}
                  >
                    {show.label}
                  </div>
                  <div
                    style={{
                      fontSize: '11px',
                      color: 'var(--color-color-10)',
                      marginBottom: '16px',
                    }}
                  >
                    {show.time}
                  </div>
                  <div
                    style={{
                      fontFamily: 'Poppins, sans-serif',
                      fontSize: '28px',
                      fontWeight: 600,
                      color: 'var(--color-blue-1)',
                      marginBottom: '12px',
                    }}
                  >
                    ₹{showPrice}
                  </div>
                  <button
                    style={{
                      width: '100%',
                      padding: '8px',
                      background: 'white',
                      border: '1px solid var(--color-gray-800)',
                      borderRadius: '6px',
                      fontSize: '12px',
                      color: 'var(--color-color-10)',
                      cursor: 'pointer',
                    }}
                  >
                    Edit Price
                  </button>
                </div>
              );
            })}
          </div>

          {/* Weekly Summary */}
          <div
            style={{
              marginTop: '24px',
              padding: '20px',
              background: 'var(--color-color-6)',
              borderRadius: '12px',
            }}
          >
            <h4
              style={{
                fontSize: '14px',
                fontWeight: 600,
                color: 'var(--color-blue-11)',
                marginBottom: '16px',
              }}
            >
              Weekly Price Summary
            </h4>
            <div style={{ display: 'flex', gap: '24px' }}>
              {[
                { label: 'Avg. Ticket Price', value: `₹${Math.round(selectedScreen.basePrice * 1.1)}` },
                { label: 'Highest Price', value: `₹${Math.round(selectedScreen.basePrice * 1.2) + 50}` },
                { label: 'Lowest Price', value: `₹${selectedScreen.basePrice}` },
                { label: 'Most Preferred', value: 'Show 2' },
              ].map((stat, i) => (
                <div key={i} style={{ flex: 1 }}>
                  <div style={{ fontSize: '12px', color: 'var(--color-color-10)', marginBottom: '4px' }}>
                    {stat.label}
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-blue-11)' }}>
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

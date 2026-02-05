import React from 'react';

const halls = [
  {
    id: 'hall-a',
    name: 'Hall A',
    capacity: 200,
    status: 'occupied',
    currentEvent: 'Corporate Workshop',
    timeSlot: '9:30 - 11:45',
    nextAvailable: '12:00 PM',
  },
  {
    id: 'hall-b',
    name: 'Hall B',
    capacity: 150,
    status: 'occupied',
    currentEvent: 'Team Building Event',
    timeSlot: '9:30 - 11:45',
    nextAvailable: '12:00 PM',
  },
  {
    id: 'conference',
    name: 'Conference Room',
    capacity: 50,
    status: 'available',
    currentEvent: null,
    timeSlot: null,
    nextAvailable: 'Now',
  },
  {
    id: 'auditorium',
    name: 'Auditorium',
    capacity: 500,
    status: 'occupied',
    currentEvent: 'Annual Meeting',
    timeSlot: '1:30 - 3:00',
    nextAvailable: '3:30 PM',
  },
];

function HallCard({ hall }) {
  const statusColors = {
    available: { bg: 'rgba(33, 150, 83, 0.1)', text: 'var(--color-green)', label: 'Available' },
    occupied: { bg: 'rgba(29, 82, 243, 0.1)', text: 'var(--color-blue-1)', label: 'Running' },
    maintenance: { bg: 'rgba(242, 132, 2, 0.1)', text: 'var(--color-red-14)', label: 'Maintenance' },
  };

  const status = statusColors[hall.status];

  return (
    <div
      style={{
        background: 'white',
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <div>
          <h3
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
              margin: 0,
            }}
          >
            {hall.name}
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            Capacity: {hall.capacity} people
          </p>
        </div>
        <span
          style={{
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 500,
            background: status.bg,
            color: status.text,
          }}
        >
          {status.label}
        </span>
      </div>

      {/* Current Event */}
      {hall.currentEvent ? (
        <div
          style={{
            padding: '16px',
            background: 'var(--color-color-6)',
            borderRadius: '12px',
            borderLeft: `4px solid ${status.text}`,
          }}
        >
          <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--color-blue-11)' }}>
            {hall.currentEvent}
          </div>
          <div style={{ fontSize: '13px', color: 'var(--color-color-10)', marginTop: '4px' }}>
            {hall.timeSlot}
          </div>
        </div>
      ) : (
        <div
          style={{
            padding: '16px',
            background: 'var(--color-color-6)',
            borderRadius: '12px',
            textAlign: 'center',
            color: 'var(--color-color-10)',
            fontSize: '14px',
          }}
        >
          No current booking
        </div>
      )}

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '12px', color: 'var(--color-gray-9)' }}>
          Next available: {hall.nextAvailable}
        </span>
        <button
          style={{
            padding: '8px 16px',
            background: hall.status === 'available' ? 'var(--color-blue-1)' : 'transparent',
            color: hall.status === 'available' ? 'white' : 'var(--color-blue-1)',
            border: hall.status === 'available' ? 'none' : '1px solid var(--color-blue-1)',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          {hall.status === 'available' ? 'Book Now' : 'View Details'}
        </button>
      </div>
    </div>
  );
}

export default function HallManagement() {
  const occupiedCount = halls.filter((h) => h.status === 'occupied').length;

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
            Hall Management
          </h1>
          <p style={{ color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            15 September 2023, Friday
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Occupancy Indicator */}
          <div
            style={{
              background: 'white',
              padding: '12px 20px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <span style={{ fontSize: '14px', color: 'var(--color-color-10)' }}>Occupancy</span>
            <span
              style={{
                fontFamily: 'Poppins, sans-serif',
                fontSize: '18px',
                fontWeight: 600,
                color: 'var(--color-blue-1)',
              }}
            >
              {occupiedCount}/{halls.length}
            </span>
          </div>

          <button
            style={{
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
            + Add Hall
          </button>
        </div>
      </div>

      {/* Halls Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '20px',
        }}
      >
        {halls.map((hall) => (
          <HallCard key={hall.id} hall={hall} />
        ))}
      </div>

      {/* Quick Stats */}
      <div
        style={{
          marginTop: '24px',
          background: 'white',
          borderRadius: '16px',
          padding: '24px',
        }}
      >
        <h2
          style={{
            fontFamily: 'Poppins, sans-serif',
            fontSize: '18px',
            fontWeight: 600,
            color: 'var(--color-blue-11)',
            marginBottom: '20px',
          }}
        >
          Today's Schedule Overview
        </h2>
        <div style={{ display: 'flex', gap: '20px' }}>
          {[
            { time: '9:30 - 11:45', count: 2, label: 'Morning Sessions' },
            { time: '12:00 - 1:00', count: 0, label: 'Lunch Break' },
            { time: '1:30 - 3:00', count: 1, label: 'Afternoon Sessions' },
            { time: '3:30 - 5:00', count: 2, label: 'Evening Sessions' },
          ].map((slot, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                padding: '16px',
                background: 'var(--color-color-6)',
                borderRadius: '12px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '13px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
                {slot.time}
              </div>
              <div
                style={{
                  fontFamily: 'Poppins, sans-serif',
                  fontSize: '24px',
                  fontWeight: 600,
                  color: slot.count > 0 ? 'var(--color-blue-1)' : 'var(--color-gray-9)',
                }}
              >
                {slot.count}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--color-gray-9)', marginTop: '4px' }}>
                {slot.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

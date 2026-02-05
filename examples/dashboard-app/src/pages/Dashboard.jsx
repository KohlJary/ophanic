import React from 'react';

const stats = [
  { label: 'Total Revenue', value: '₹2,45,000', change: '+12%', trend: 'up' },
  { label: 'Total Bookings', value: '1,234', change: '+8%', trend: 'up' },
  { label: 'Avg. Occupancy', value: '78%', change: '+5%', trend: 'up' },
  { label: 'Active Screens', value: '4/4', change: '0%', trend: 'neutral' },
];

const recentActivity = [
  { time: '2:30 PM', event: 'Screen 1 - Show started', type: 'info' },
  { time: '2:15 PM', event: 'New booking: 5 tickets', type: 'success' },
  { time: '1:45 PM', event: 'Price updated for evening shows', type: 'warning' },
  { time: '12:30 PM', event: 'Hall A maintenance completed', type: 'success' },
];

function StatCard({ label, value, change, trend }) {
  const trendColors = {
    up: 'var(--color-green)',
    down: 'var(--color-red)',
    neutral: 'var(--color-gray-500)',
  };

  return (
    <div
      style={{
        background: 'white',
        borderRadius: '16px',
        padding: '24px',
        flex: 1,
      }}
    >
      <div style={{ fontSize: '14px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
        {label}
      </div>
      <div
        style={{
          fontFamily: 'Poppins, sans-serif',
          fontSize: '28px',
          fontWeight: 600,
          color: 'var(--color-blue-11)',
          marginBottom: '8px',
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: '13px', color: trendColors[trend] }}>
        {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '–'} {change} from last week
      </div>
    </div>
  );
}

export default function Dashboard() {
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
            Dashboard
          </h1>
          <p style={{ color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            15 September 2023, 4:50 pm
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              background: 'white',
              padding: '10px 16px',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: '1px solid var(--color-gray-18)',
            }}
          >
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search anything..."
              style={{
                border: 'none',
                outline: 'none',
                fontSize: '14px',
                width: '180px',
              }}
            />
          </div>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
          >
            🔔
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '24px' }}>
        {stats.map((stat, i) => (
          <StatCard key={i} {...stat} />
        ))}
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Statistics Chart Placeholder */}
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
            <h2
              style={{
                fontFamily: 'Poppins, sans-serif',
                fontSize: '18px',
                fontWeight: 600,
                color: 'var(--color-blue-11)',
                margin: 0,
              }}
            >
              Statistics
            </h2>
            <button
              style={{
                padding: '8px 16px',
                background: 'var(--color-color-6)',
                border: 'none',
                borderRadius: '8px',
                fontSize: '13px',
                color: 'var(--color-color-10)',
                cursor: 'pointer',
              }}
            >
              This Week ▾
            </button>
          </div>
          <div
            style={{
              height: '200px',
              background: 'var(--color-color-6)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-gray-500)',
            }}
          >
            Chart placeholder - Revenue & Bookings over time
          </div>
          <div style={{ marginTop: '16px', fontSize: '13px', color: 'var(--color-color-10)' }}>
            Statistics details
          </div>
        </div>

        {/* Recent Activity */}
        <div
          style={{
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
            Recent Activity
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {recentActivity.map((activity, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  padding: '12px',
                  background: 'var(--color-color-6)',
                  borderRadius: '10px',
                }}
              >
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background:
                      activity.type === 'success'
                        ? 'var(--color-green)'
                        : activity.type === 'warning'
                        ? 'var(--color-red-14)'
                        : 'var(--color-blue-1)',
                    marginTop: '6px',
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', color: 'var(--color-blue-11)' }}>
                    {activity.event}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--color-gray-9)', marginTop: '4px' }}>
                    {activity.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tasks Section */}
      <div
        style={{
          marginTop: '20px',
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
          Today's Tasks
        </h2>
        <div style={{ display: 'flex', gap: '16px' }}>
          {[
            { title: 'Infra. Audit', status: 'In Progress', priority: 'High' },
            { title: 'Update Pricing', status: 'Pending', priority: 'Medium' },
            { title: 'Staff Training', status: 'Completed', priority: 'Low' },
          ].map((task, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                padding: '16px',
                background: 'var(--color-color-6)',
                borderRadius: '12px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '12px',
                }}
              >
                <span
                  style={{
                    fontSize: '12px',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    background:
                      task.priority === 'High'
                        ? 'rgba(246, 32, 32, 0.1)'
                        : task.priority === 'Medium'
                        ? 'rgba(242, 132, 2, 0.1)'
                        : 'rgba(33, 150, 83, 0.1)',
                    color:
                      task.priority === 'High'
                        ? 'var(--color-red)'
                        : task.priority === 'Medium'
                        ? 'var(--color-red-14)'
                        : 'var(--color-green)',
                  }}
                >
                  {task.priority}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--color-gray-9)' }}>{task.status}</span>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--color-blue-11)' }}>
                {task.title}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

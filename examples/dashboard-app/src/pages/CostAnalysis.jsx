import React from 'react';

const expenseCategories = [
  { name: 'Staff Salaries', amount: 85000, percentage: 35 },
  { name: 'Maintenance', amount: 45000, percentage: 18 },
  { name: 'Utilities', amount: 32000, percentage: 13 },
  { name: 'Marketing', amount: 28000, percentage: 11 },
  { name: 'Licensing', amount: 25000, percentage: 10 },
  { name: 'Others', amount: 30000, percentage: 13 },
];

const revenueStreams = [
  { name: 'Ticket Sales', amount: 185000, percentage: 65 },
  { name: 'F&B', amount: 58000, percentage: 20 },
  { name: 'Advertising', amount: 28000, percentage: 10 },
  { name: 'Events', amount: 14000, percentage: 5 },
];

export default function CostAnalysis() {
  const totalExpenses = expenseCategories.reduce((sum, cat) => sum + cat.amount, 0);
  const totalRevenue = revenueStreams.reduce((sum, stream) => sum + stream.amount, 0);
  const profit = totalRevenue - totalExpenses;

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
            Cost Analysis
          </h1>
          <p style={{ color: 'var(--color-color-10)', margin: '4px 0 0' }}>
            September 2023 Financial Overview
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            style={{
              padding: '10px 20px',
              background: 'white',
              border: '1px solid var(--color-gray-18)',
              borderRadius: '8px',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            Export PDF
          </button>
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
            Add Expense
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
        <div style={{ background: 'white', borderRadius: '16px', padding: '24px' }}>
          <div style={{ fontSize: '14px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
            Total Revenue
          </div>
          <div
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '28px',
              fontWeight: 600,
              color: 'var(--color-green)',
            }}
          >
            ₹{totalRevenue.toLocaleString()}
          </div>
        </div>
        <div style={{ background: 'white', borderRadius: '16px', padding: '24px' }}>
          <div style={{ fontSize: '14px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
            Total Expenses
          </div>
          <div
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '28px',
              fontWeight: 600,
              color: 'var(--color-red)',
            }}
          >
            ₹{totalExpenses.toLocaleString()}
          </div>
        </div>
        <div style={{ background: 'white', borderRadius: '16px', padding: '24px' }}>
          <div style={{ fontSize: '14px', color: 'var(--color-color-10)', marginBottom: '8px' }}>
            Net Profit
          </div>
          <div
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '28px',
              fontWeight: 600,
              color: profit > 0 ? 'var(--color-green)' : 'var(--color-red)',
            }}
          >
            ₹{profit.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Breakdown Tables */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Expenses Table */}
        <div style={{ background: 'white', borderRadius: '16px', padding: '24px' }}>
          <h2
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
              marginBottom: '20px',
            }}
          >
            Expense Breakdown
          </h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>Category</th>
                <th style={{ textAlign: 'right', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>Amount</th>
                <th style={{ textAlign: 'right', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>%</th>
              </tr>
            </thead>
            <tbody>
              {expenseCategories.map((cat, i) => (
                <tr key={i}>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px' }}>{cat.name}</td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px', textAlign: 'right' }}>₹{cat.amount.toLocaleString()}</td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px', textAlign: 'right', color: 'var(--color-color-10)' }}>{cat.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Revenue Table */}
        <div style={{ background: 'white', borderRadius: '16px', padding: '24px' }}>
          <h2
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-blue-11)',
              marginBottom: '20px',
            }}
          >
            Revenue Streams
          </h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>Source</th>
                <th style={{ textAlign: 'right', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>Amount</th>
                <th style={{ textAlign: 'right', padding: '12px 8px', borderBottom: '1px solid var(--color-gray-18)', fontSize: '13px', color: 'var(--color-color-10)' }}>%</th>
              </tr>
            </thead>
            <tbody>
              {revenueStreams.map((stream, i) => (
                <tr key={i}>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px' }}>{stream.name}</td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px', textAlign: 'right' }}>₹{stream.amount.toLocaleString()}</td>
                  <td style={{ padding: '12px 8px', borderBottom: '1px solid var(--color-color-6)', fontSize: '14px', textAlign: 'right', color: 'var(--color-color-10)' }}>{stream.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Monthly Trend */}
      <div style={{ marginTop: '20px', background: 'white', borderRadius: '16px', padding: '24px' }}>
        <h2
          style={{
            fontFamily: 'Poppins, sans-serif',
            fontSize: '18px',
            fontWeight: 600,
            color: 'var(--color-blue-11)',
            marginBottom: '20px',
          }}
        >
          Monthly Trend
        </h2>
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
          Chart placeholder - Revenue vs Expenses trend
        </div>
      </div>
    </div>
  );
}

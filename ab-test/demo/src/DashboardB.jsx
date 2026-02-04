// Attempt B: Implementation from Ophanic diagram

function MetricCard({ icon, label, value, trend, up }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm flex items-center gap-4">
      {/* Icon block - vertically centered */}
      <div className="text-4xl w-14 h-14 flex items-center justify-center bg-gray-50 rounded-lg">
        {icon}
      </div>
      {/* Text block - label/value/trend stacked */}
      <div className="flex flex-col">
        <span className="text-sm text-gray-500">{label}</span>
        <span className="text-2xl font-bold">{value}</span>
        <span className={`text-sm ${up ? 'text-green-500' : 'text-red-500'}`}>
          {up ? '↑' : '↓'} {trend}
        </span>
      </div>
    </div>
  );
}

function ActivityFeed() {
  const items = [
    { name: 'John', action: 'created order', time: '2m ago' },
    { name: 'Sarah', action: 'updated prof', time: '5m ago' },
    { name: 'Mike', action: 'left comment', time: '12m ago' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm h-full">
      {/* Header row: title left, link right */}
      <div className="flex justify-between items-center p-4 border-b">
        <h3 className="font-semibold">Activity</h3>
        <a href="#" className="text-blue-500 text-sm hover:underline">View All →</a>
      </div>
      {/* Activity items */}
      <div className="p-4 flex flex-col gap-3">
        {items.map((item, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
            <div className="flex-1 min-w-0">
              <span className="text-sm">
                <strong>{item.name}</strong> {item.action}
              </span>
            </div>
            <span className="text-xs text-gray-400 flex-shrink-0">{item.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Calendar() {
  const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const today = 4;
  const daysInMonth = 28;

  return (
    <div className="bg-white rounded-lg shadow-sm h-full">
      {/* Month nav header */}
      <div className="flex justify-between items-center p-4 border-b">
        <button className="hover:bg-gray-100 p-1 rounded">←</button>
        <span className="font-semibold">February 2026</span>
        <button className="hover:bg-gray-100 p-1 rounded">→</button>
      </div>

      {/* Calendar grid */}
      <div className="p-4">
        {/* Day headers */}
        <div className="grid grid-cols-7 gap-1 text-center text-sm text-gray-400 mb-2">
          {days.map((d, i) => <div key={i}>{d}</div>)}
        </div>

        {/* Date cells */}
        <div className="grid grid-cols-7 gap-1 text-center text-sm">
          {[...Array(daysInMonth)].map((_, i) => {
            const day = i + 1;
            const isToday = day === today;
            return (
              <div
                key={day}
                className={`p-1 rounded ${isToday ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
              >
                {day}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function DashboardB() {
  return (
    <div className="min-h-screen bg-gray-100 pb-20">
      {/* Header - full width, logo left, notifications+avatar right */}
      <header className="bg-white h-16 px-6 flex items-center justify-between shadow-sm">
        <div className="text-xl font-bold">LOGO</div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <span className="text-xl">🔔</span>
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">3</span>
          </div>
          <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
        </div>
      </header>

      {/* Main area: Sidebar + Content */}
      {/* From diagram: Sidebar ~15 chars, Content ~60 chars → 20%/80% */}
      <div className="flex">
        {/* Sidebar - visible on desktop, icons on tablet, bottom nav on mobile */}
        <aside className="hidden md:flex md:flex-col md:w-[20%] bg-white min-h-[calc(100vh-4rem)] p-4 shadow-sm">
          {/* Desktop: full text */}
          <nav className="hidden lg:flex flex-col gap-2">
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Dashboard</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Analytics</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Reports</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Settings</a>
          </nav>
          {/* Tablet: icons only */}
          <nav className="lg:hidden flex flex-col gap-4 items-center pt-2">
            <span className="text-xl">📊</span>
            <span className="text-xl">📈</span>
            <span className="text-xl">📋</span>
            <span className="text-xl">⚙️</span>
          </nav>
        </aside>

        {/* Main Content - 80% on desktop */}
        <main className="flex-1 p-6">
          {/* Metric Cards Row - 3 equal columns, stack on mobile */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <MetricCard icon="📈" label="Revenue" value="$24,500" trend="+12%" up />
            <MetricCard icon="👥" label="Users" value="1,234" trend="+5%" up />
            <MetricCard icon="📦" label="Orders" value="456" trend="-2%" up={false} />
          </div>

          {/* Chart + Activity Feed Row */}
          {/* From diagram: Chart ~35 chars, Activity ~17 chars → 65%/35% */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="lg:w-[65%] bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">CHART</h3>
              <div className="h-64 bg-gray-50 rounded flex items-center justify-center text-gray-400">
                [chart]
              </div>
            </div>
            <div className="lg:w-[35%]">
              <ActivityFeed />
            </div>
          </div>

          {/* Table + Calendar Row */}
          {/* From diagram: Table ~40 chars, Calendar ~15 chars → 70%/30% */}
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="lg:w-[70%] bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">TABLE</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">Order</th>
                    <th className="pb-2">Customer</th>
                    <th className="pb-2">Amount</th>
                    <th className="pb-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-100">
                    <td className="py-2">#001</td>
                    <td>Alice</td>
                    <td>$120</td>
                    <td>Shipped</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-2">#002</td>
                    <td>Bob</td>
                    <td>$85</td>
                    <td>Pending</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="lg:w-[30%]">
              <Calendar />
            </div>
          </div>
        </main>
      </div>

      {/* Mobile bottom nav - visible only on mobile */}
      <nav className="md:hidden fixed bottom-14 left-0 right-0 bg-white border-t flex justify-around py-3">
        <span className="text-xl">📊</span>
        <span className="text-xl">📈</span>
        <span className="text-xl">📋</span>
        <span className="text-xl">⚙️</span>
      </nav>
    </div>
  );
}

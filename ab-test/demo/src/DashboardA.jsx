// Attempt A: Implementation from text spec only (no Ophanic diagram)

function MetricCard({ icon, label, value, trend, up }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm flex items-center">
      <div className="text-3xl mr-4">{icon}</div>
      <div>
        <div className="text-gray-500 text-sm">{label}</div>
        <div className="text-2xl font-bold">{value}</div>
        <div className={`text-sm ${up ? 'text-green-500' : 'text-red-500'}`}>
          {up ? '↑' : '↓'} {trend}
        </div>
      </div>
    </div>
  );
}

function ActivityItem({ name, action, time }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
      <div>
        <div className="text-sm"><strong>{name}</strong> {action}</div>
        <div className="text-xs text-gray-400">{time}</div>
      </div>
    </div>
  );
}

function CalendarWidget() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <button>←</button>
        <span className="font-semibold">February 2026</span>
        <button>→</button>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-sm">
        <div className="text-gray-400">S</div>
        <div className="text-gray-400">M</div>
        <div className="text-gray-400">T</div>
        <div className="text-gray-400">W</div>
        <div className="text-gray-400">T</div>
        <div className="text-gray-400">F</div>
        <div className="text-gray-400">S</div>
        {[...Array(28)].map((_, i) => (
          <div key={i} className={i + 1 === 4 ? 'bg-blue-500 text-white rounded' : ''}>
            {i + 1}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DashboardA() {
  return (
    <div className="min-h-screen bg-gray-100 pb-20">
      {/* Header */}
      <header className="bg-white h-16 px-6 flex items-center justify-between shadow-sm">
        <div className="text-xl font-bold">Logo</div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <span className="text-xl">🔔</span>
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">3</span>
          </div>
          <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-1/5 bg-white min-h-screen p-4 shadow-sm">
          <nav className="flex flex-col gap-2">
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Dashboard</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Analytics</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Reports</a>
            <a href="#" className="p-2 hover:bg-gray-100 rounded">Settings</a>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {/* Metric Cards Row */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <MetricCard icon="📈" label="Revenue" value="$24,500" trend="+12%" up />
            <MetricCard icon="👥" label="Users" value="1,234" trend="+5%" up />
            <MetricCard icon="📦" label="Orders" value="456" trend="-2%" up={false} />
          </div>

          {/* Chart + Activity Feed Row */}
          <div className="flex gap-4 mb-6">
            <div className="w-2/3 bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">Revenue Chart</h3>
              <div className="h-64 bg-gray-50 rounded flex items-center justify-center">
                [Chart Placeholder]
              </div>
            </div>
            <div className="w-1/3 bg-white p-4 rounded-lg shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold">Activity</h3>
                <a href="#" className="text-blue-500 text-sm">View All</a>
              </div>
              <div className="flex flex-col gap-3">
                <ActivityItem name="John" action="created a new order" time="2m ago" />
                <ActivityItem name="Sarah" action="updated profile" time="5m ago" />
                <ActivityItem name="Mike" action="left a comment" time="12m ago" />
              </div>
            </div>
          </div>

          {/* Table + Calendar Row */}
          <div className="flex gap-4">
            <div className="w-2/3 bg-white p-4 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">Recent Orders</h3>
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-500 text-sm">
                    <th className="pb-2">Order</th>
                    <th className="pb-2">Customer</th>
                    <th className="pb-2">Amount</th>
                    <th className="pb-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>#001</td><td>Alice</td><td>$120</td><td>Shipped</td></tr>
                  <tr><td>#002</td><td>Bob</td><td>$85</td><td>Pending</td></tr>
                </tbody>
              </table>
            </div>
            <div className="w-1/3 bg-white p-4 rounded-lg shadow-sm">
              <CalendarWidget />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

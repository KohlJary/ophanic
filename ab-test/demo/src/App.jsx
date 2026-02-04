import { useState } from 'react'
import DashboardA from './DashboardA'
import DashboardB from './DashboardB'

function App() {
  const [version, setVersion] = useState('A')

  return (
    <div>
      {version === 'A' ? <DashboardA /> : <DashboardB />}

      {/* Sticky footer toggle */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white px-6 py-3 flex items-center justify-between z-50">
        <div className="text-sm">
          <span className="font-semibold">Ophanic A/B Test</span>
          <span className="text-gray-400 ml-2">
            {version === 'A' ? 'Without diagram (text spec only)' : 'With Ophanic diagram'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setVersion('A')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition ${
              version === 'A'
                ? 'bg-red-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            A: No Diagram
          </button>
          <button
            onClick={() => setVersion('B')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition ${
              version === 'B'
                ? 'bg-green-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            B: With Ophanic
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

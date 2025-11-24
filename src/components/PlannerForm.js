// frontend/src/components/PlannerForm.js
"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const TRAVEL_TYPES = ['city', 'beach', 'adventure', 'culture'];

export default function PlannerForm() {
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [budget, setBudget] = useState(5000000);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const [travelType, setTravelType] = useState('city');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Hardcode user_id dan travelers untuk PoC sederhana
    const payload = {
      user_id: "user_mock_001", 
      destination,
      start_date: startDate,
      end_date: endDate,
      budget_idr: parseInt(budget),
      travelers: 1,
      travel_type: travelType,
      preferences: "prefer homestay"
    };

    try {
      const response = await fetch(`${API_URL}/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.plan_id) {
        // Arahkan ke halaman review itinerary
        router.push(`/plan/${data.plan_id}`); 
      } else {
        alert(`Error: ${data.message || 'Failed to generate plan'}`);
      }
    } catch (error) {
      alert(`Network Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 max-w-lg mx-auto bg-white rounded-xl shadow-md space-y-4">
      <h2 className="text-xl font-bold">🗺️ Rencanakan Liburan Anda</h2>
      
      {/* Input Destinasi */}
      <div>
        <label htmlFor="destination" className="block text-sm font-medium text-gray-700">Destinasi</label>
        <input
          type="text"
          id="destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      {/* Input Tanggal */}
      <div className="flex space-x-4">
        <div>
          <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Mulai Tanggal</label>
          <input
            type="date"
            id="start_date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">Sampai Tanggal</label>
          <input
            type="date"
            id="end_date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
      </div>

      {/* Input Budget */}
      <div>
        <label htmlFor="budget" className="block text-sm font-medium text-gray-700">Budget Total (IDR)</label>
        <input
          type="number"
          id="budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          min="1000000"
          required
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Jenis Liburan</label>
        <div className="mt-2 flex flex-wrap gap-3">
          {TRAVEL_TYPES.map(type => (
            <button
              key={type}
              type="button" // Penting: Jangan submit form
              onClick={() => setTravelType(type)}
              className={`px-3 py-1 text-sm font-medium rounded-full transition-colors 
                ${travelType === type 
                  ? 'bg-indigo-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
              `}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Generate Itinerary'}
      </button>
    </form>
  );
}
"use client";

import React, { useState, useEffect, useCallback } from 'react';
// IMPOR: Path relatif ini bergantung pada BookingHistory berada di frontend/src/components/
import BookingHistory from '@/components/BookingHistory'; 

// URL API diambil dari .env.local di folder frontend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const USER_ID = "user_1"; // Hardcode User ID untuk PoC

// Daftar jenis liburan untuk UX yang lebih baik
const TRAVEL_TYPES = ['city', 'beach', 'adventure', 'culture', 'nature', 'kuliner'];

// --- Komponen PlanningForm ---
const PlanningForm = ({ onPlanGenerated }) => {
    const [destination, setDestination] = useState('Yogyakarta');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [budget, setBudget] = useState(5000000);
    const [travelType, setTravelType] = useState('culture');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (new Date(startDate) >= new Date(endDate)) {
            setError("Tanggal Mulai harus sebelum Tanggal Selesai.");
            setLoading(false);
            return;
        }

        const payload = {
            user_id: USER_ID,
            destination,
            start_date: startDate,
            end_date: endDate,
            budget_idr: parseInt(budget),
            travelers: 1,
            travel_type: travelType,
            preferences: `Suka ${travelType} dan hotel dengan rating bagus.`
        };

        try {
            const response = await fetch(`${API_BASE_URL}/plan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                onPlanGenerated(data);
            } else {
                setError(data.message || 'Gagal memanggil Agen LLM.');
            }
        } catch (error) {
            setError(`Network Error: Tidak dapat terhubung ke Backend API. Pastikan Docker berjalan di ${API_BASE_URL}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-lg mx-auto p-6 bg-white rounded-xl shadow-lg border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span role="img" aria-label="map">🗺️</span> Rencanakan Liburan Anda
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                    <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}

                <div>
                    <label htmlFor="destination" className="block text-sm font-medium text-gray-700">Destinasi (Contoh: Yogyakarta)</label>
                    <input
                        type="text"
                        id="destination"
                        value={destination}
                        onChange={(e) => setDestination(e.target.value)}
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Jenis Liburan</label>
                    <div className="flex flex-wrap gap-2">
                        {TRAVEL_TYPES.map(type => (
                            <button
                                key={type}
                                type="button"
                                onClick={() => setTravelType(type)}
                                className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
                                    travelType === type 
                                      ? 'bg-indigo-600 text-white shadow-md' 
                                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                {type.charAt(0).toUpperCase() + type.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex space-x-4">
                    <div className="flex-1">
                        <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Mulai Tanggal</label>
                        <input
                            type="date"
                            id="start_date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3"
                        />
                    </div>
                    <div className="flex-1">
                        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">Sampai Tanggal</label>
                        <input
                            type="date"
                            id="end_date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3"
                        />
                    </div>
                </div>

                <div>
                    <label htmlFor="budget" className="block text-sm font-medium text-gray-700">Budget Total (IDR)</label>
                    <input
                        type="number"
                        id="budget"
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        min="1000000"
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3"
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 px-4 border border-transparent rounded-lg shadow-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                    {loading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Agen LLM Sedang Merencanakan...
                        </span>
                    ) : 'Generate Itinerary'}
                </button>
            </form>
        </div>
    );
};

// --- Komponen ItineraryDisplay ---
const ItineraryDisplay = ({ plan, onBookingConfirmed }) => {
    const [showBookingModal, setShowBookingModal] = useState(false);
    
    if (!plan.itinerary) {
        return (
            <div className="text-center p-8 bg-yellow-50 border-yellow-300 border rounded-lg max-w-3xl mx-auto">
                <h3 className="text-xl font-semibold text-yellow-800">Rencana Gagal Dibuat</h3>
                <p className="mt-2 text-yellow-700">Agen LLM gagal membuat rencana yang terstruktur. Coba ganti preferensi atau tanggal.</p>
                <p className="text-sm mt-1 text-gray-500">Pesan dari API: {plan.message}</p>
            </div>
        );
    }

    const { trip_name, destination, start_date, end_date, days, total_estimated_cost } = plan.itinerary;

    const formatRupiah = (amount) => new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
    
    const safeTotalCost = total_estimated_cost || 0;

    return (
        <div className="max-w-4xl mx-auto space-y-8 p-6 bg-white rounded-xl shadow-lg">
            <h1 className="text-3xl font-bold text-center text-indigo-700">{trip_name || 'Rencana Perjalanan'}</h1>
            <div className="flex justify-between p-4 bg-indigo-50 rounded-lg text-indigo-800">
                <div>
                    <p className="font-semibold">Destinasi:</p>
                    <p>{destination}</p>
                </div>
                <div>
                    <p className="font-semibold">Tanggal:</p>
                    <p>{start_date} s/d {end_date}</p>
                </div>
                <div>
                    <p className="font-semibold">Total Estimasi Biaya:</p>
                    <p className="text-xl font-extrabold">{formatRupiah(safeTotalCost)}</p>
                </div>
            </div>

            <div className="space-y-6">
                <h3 className="text-2xl font-semibold border-b pb-2 text-gray-700">Rincian Harian</h3>
                {days?.map((day, index) => (
                    <div key={index} className="bg-gray-50 p-5 rounded-lg border-l-4 border-indigo-400 shadow-sm">
                        <strong className="text-lg font-bold text-indigo-600">
                            Hari {index + 1} — {day.date}
                        </strong>
                        <p className="text-sm text-gray-500 mb-3">Biaya Harian: {formatRupiah(day.daily_cost || 0)}</p>
                        
                        <div className="space-y-3 pl-4 border-l ml-2">
                            {day.activities?.map((act, idx) => (
                                <div key={idx} className="relative">
                                    <span className="absolute left-[-1.6rem] top-1 text-indigo-500">●</span>
                                    <p className="font-medium text-gray-800">{act.time} - {act.name}</p>
                                    <p className="text-sm text-gray-600 italic">({act.description})</p>
                                    <p className="text-xs text-green-700">{formatRupiah(act.estimated_cost || 0)}</p>
                                </div>
                            ))}
                        </div>

                        {day.lodging && (
                            <div className="mt-4 p-3 bg-white rounded-lg border">
                                <p className="font-semibold">🏨 Penginapan:</p>
                                <p className="text-sm">{day.lodging.name} ({formatRupiah(day.lodging.price || 0)} / malam)</p>
                            </div>
                        )}
                        {day.transport && (
                            <div className="mt-2 text-sm text-gray-600">
                                <p>🚗 Transportasi: {day.transport.type} (~{formatRupiah(day.transport.estimated_cost || 0)})</p>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <button 
                onClick={() => setShowBookingModal(true)}
                className="w-full py-3 px-4 rounded-lg shadow-md text-lg font-bold text-white bg-green-600 hover:bg-green-700 transition-colors"
            >
                Confirm & Book (Simulasi Transaksi)
            </button>
            
            <BookingModal 
                show={showBookingModal}
                onClose={() => setShowBookingModal(false)}
                planId={plan.plan_id}
                userId={plan.user_id}
                onBookingConfirmed={onBookingConfirmed}
                totalAmount={safeTotalCost}
            />
        </div>
    );
};

// --- Komponen BookingModal ---
const BookingModal = ({ show, onClose, planId, userId, onBookingConfirmed, totalAmount }) => {
    const [paymentToken, setPaymentToken] = useState('tok_valid_123');
    const [confirmed, setConfirmed] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const formatRupiah = (amount) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount);

    useEffect(() => {
        if (show) {
            setConfirmed(false);
            setError(null);
            setSuccess(null);
        }
    }, [show]);

    const handleConfirmBooking = async () => {
        if (!confirmed || !paymentToken) {
            setError("Anda harus mengkonfirmasi dan memberikan token pembayaran.");
            return;
        }
        
        if (!planId || !userId) {
            setError("Error: ID Rencana atau ID Pengguna hilang. Coba buat rencana baru.");
            return;
        }

        setLoading(true);
        setError(null);

        const payload = {
            user_id: userId,
            payment_token: paymentToken,
            confirmed: confirmed 
        };

        try {
            const response = await fetch(`${API_BASE_URL}/plan/${planId}/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(`Booking Berhasil! Transaksi ID: ${data.message.split(': ')[1]}`);
                onBookingConfirmed(planId); 
            } else {
                let errorMessage;
                if (response.status === 422 && data.detail && Array.isArray(data.detail)) {
                    errorMessage = data.detail.map(err => {
                        const loc = err.loc.length > 1 ? err.loc[1] : 'body';
                        return `${loc}: ${err.msg}`;
                    }).join('; ');
                } else {
                    errorMessage = data.detail?.message || data.detail?.errors?.join(', ') || 'Booking Gagal. Cek log backend.';
                }
                
                setError(`Gagal (${response.status}): ${errorMessage}`);
            }
        } catch (error) {
            setError(`Network Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 transition-opacity">
            <div className="bg-white rounded-lg p-8 w-full max-w-md shadow-2xl">
                <h3 className="text-2xl font-bold mb-4 text-red-600">💳 Konfirmasi Pembayaran</h3>
                
                {success && (
                    <div className="p-4 mb-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
                        {success}
                    </div>
                )}
                {error && !success && (
                    <div className="p-4 mb-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}

                {!success && (
                    <div className="space-y-4">
                        <p>Anda akan dikenakan biaya sebesar <span className="text-xl font-extrabold text-indigo-600">{formatRupiah(totalAmount)}</span> untuk mengkonfirmasi seluruh rencana.</p>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Token Pembayaran (Mock)</label>
                            <input
                                type="text"
                                value={paymentToken}
                                onChange={(e) => setPaymentToken(e.target.value)}
                                placeholder="Gunakan tok_valid_xxx atau tok_fail_xxx"
                                className="mt-1 block w-full border border-gray-300 rounded-lg p-3"
                            />
                            <p className="text-xs text-gray-500 mt-1">Gunakan **tok_valid_123** untuk Sukses, **tok_fail_000** untuk Gagal.</p>
                        </div>
                        
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="confirmed"
                                checked={confirmed}
                                onChange={(e) => setConfirmed(e.target.checked)}
                                className="h-4 w-4 text-green-600 border-gray-300 rounded"
                            />
                            <label htmlFor="confirmed" className="ml-2 block text-sm font-medium text-gray-900">
                                Saya mengkonfirmasi dan mengizinkan booking dan pemrosesan pembayaran.
                            </label>
                        </div>

                        <button 
                            onClick={handleConfirmBooking}
                            disabled={loading || !confirmed}
                            className="w-full py-3 px-4 rounded-lg shadow-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 transition-colors"
                        >
                            {loading ? 'Memproses Transaksi...' : `Bayar ${formatRupiah(totalAmount)}`}
                        </button>
                    </div>
                )}
                <button 
                    onClick={onClose}
                    className="mt-4 w-full py-2 text-sm text-gray-600 hover:text-gray-800"
                >
                    Tutup
                </button>
            </div>
        </div>
    );
};


// --- Komponen PlannerTab ---
const PlannerTab = () => {
    const [currentPlan, setCurrentPlan] = useState(null);

    const handlePlanGenerated = (planData) => {
        setCurrentPlan(planData);
    };

    const handleBookingConfirmed = useCallback(() => {
        setCurrentPlan(prevPlan => ({
            ...prevPlan,
            status: 'confirmed',
            message: 'Booking berhasil dikonfirmasi!'
        }));
    }, []);

    return (
        <div className="py-8">
            <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-8">AI Vacation Planner</h1>
            
            {!currentPlan || currentPlan.status === 'confirmed' ? (
                // Tampilkan form jika belum ada rencana atau rencana sudah dikonfirmasi
                <>
                    <PlanningForm onPlanGenerated={handlePlanGenerated} />
                    {currentPlan && currentPlan.status === 'confirmed' && (
                        <div className="mt-6 p-4 max-w-lg mx-auto bg-green-100 border border-green-400 text-green-700 rounded-lg text-center">
                            ✅ Booking untuk Plan {currentPlan.plan_id} berhasil dikonfirmasi! Lihat di tab History.
                        </div>
                    )}
                </>
            ) : (
                // Tampilkan Itinerary untuk review
                <>
                    <ItineraryDisplay 
                        plan={currentPlan} 
                        onBookingConfirmed={handleBookingConfirmed}
                    />
                    <button
                        onClick={() => setCurrentPlan(null)}
                        className="mt-8 mx-auto block text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                        &larr; Buat Rencana Baru
                    </button>
                </>
            )}
        </div>
    );
};

// --- Komponen Utama: App Shell ---
const App = () => {
    const [activeTab, setActiveTab] = useState('planner'); // 'planner' atau 'history'

    return (
        <main className="min-h-screen p-4 sm:p-8 bg-gray-50">
            <div className="max-w-6xl mx-auto bg-white shadow-xl rounded-xl p-4 sm:p-6">
                
                {/* Header dan Navigasi Tab */}
                <div className="border-b border-gray-200">
                    <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                        <button
                            onClick={() => setActiveTab('planner')}
                            className={`py-3 px-1 text-sm font-medium ${
                                activeTab === 'planner'
                                    ? 'border-indigo-500 text-indigo-600 border-b-2'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2'
                            }`}
                        >
                            Planner (Buat Rencana)
                        </button>
                        <button
                            onClick={() => setActiveTab('history')}
                            className={`py-3 px-1 text-sm font-medium ${
                                activeTab === 'history'
                                    ? 'border-indigo-500 text-indigo-600 border-b-2'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2'
                            }`}
                        >
                            Booking History
                        </button>
                    </nav>
                </div>

                {/* Konten Tab */}
                <div className="pt-6">
                    {activeTab === 'planner' && <PlannerTab />}
                    {activeTab === 'history' && <BookingHistory userId={USER_ID} />}
                </div>
            </div>
        </main>
    );
};

export default App;
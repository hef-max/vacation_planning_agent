"use client";

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Format Rupiah
const formatRupiah = (amount) => new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
}).format(amount);

// --- BookingHistory Component ---
const BookingHistory = ({ userId }) => {
    const [summary, setSummary] = useState(null);
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!userId) {
            setError("User ID tidak ditemukan.");
            setLoading(false);
            return;
        }

        const fetchHistory = async () => {
            setLoading(true);
            setError(null);
            
            try {
                // Fetch Summary
                const summaryRes = await fetch(`${API_BASE_URL}/bookings/user/${userId}/summary`);
                const summaryData = await summaryRes.json();
                setSummary(summaryData);

                // Fetch All Bookings
                const bookingsRes = await fetch(`${API_BASE_URL}/bookings?user_id=${userId}&limit=20`);
                const bookingsData = await bookingsRes.json();
                setBookings(bookingsData);

            } catch (err) {
                setError(`Gagal mengambil data riwayat. Pastikan backend berjalan.`);
                console.error("Fetch history error:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [userId]);

    if (loading) {
        return <div className="text-center p-10 text-lg font-medium text-indigo-600">Memuat Riwayat Booking...</div>;
    }

    if (error) {
        return <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg max-w-4xl mx-auto">{error}</div>;
    }

    const confirmedBookings = bookings.filter(b => b.status === 'CONFIRMED');

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800">Riwayat & Ringkasan Keuangan</h2>

            {/* Ringkasan Keuangan */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <SummaryCard title="Total Booking" value={summary?.total_bookings || 0} icon="📅" />
                <SummaryCard title="Total Pengeluaran" value={formatRupiah(summary?.total_spent_idr || 0)} icon="💸" />
                <SummaryCard title="Status Dikonfirmasi" value={confirmedBookings.length} icon="✅" />
            </div>

            {/* Daftar Booking */}
            <div className="space-y-4">
                <h3 className="text-xl font-semibold border-b pb-2">Daftar Transaksi ({confirmedBookings.length} Dikonfirmasi)</h3>
                
                {confirmedBookings.length === 0 ? (
                    <div className="p-6 bg-gray-100 rounded-lg text-center text-gray-500">
                        Belum ada booking yang dikonfirmasi. Buat rencana baru di tab Planner!
                    </div>
                ) : (
                    confirmedBookings.map((booking) => (
                        <BookingItem key={booking.booking_id} booking={booking} />
                    ))
                )}
            </div>
        </div>
    );
};

// --- Komponen Pembantu ---
const SummaryCard = ({ title, value, icon }) => (
    <div className="bg-indigo-50 p-5 rounded-xl shadow-sm flex items-center justify-between">
        <div>
            <p className="text-sm font-medium text-indigo-700">{title}</p>
            <p className="text-2xl font-extrabold text-indigo-800 mt-1">{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
    </div>
);

const BookingItem = ({ booking }) => (
    <div className="p-4 border rounded-lg flex justify-between items-center bg-white shadow-sm">
        <div>
            <p className="font-semibold text-gray-800">{booking.booking_type.toUpperCase()} Booking</p>
            <p className="text-sm text-gray-500">Ref: {booking.provider_ref}</p>
            <p className="text-xs text-gray-400">ID: {booking.booking_id}</p>
        </div>
        <div className="text-right">
            <p className={`text-lg font-bold ${booking.status === 'CONFIRMED' ? 'text-green-600' : 'text-yellow-600'}`}>
                {formatRupiah(booking.amount_idr)}
            </p>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                booking.status === 'CONFIRMED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
                {booking.status}
            </span>
        </div>
    </div>
);

export default BookingHistory;
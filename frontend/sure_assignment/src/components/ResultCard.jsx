import React from "react";
import { Banknote, CalendarDays, CreditCard } from "lucide-react";

export default function ResultCard({ bank, fields }) {
  const transactions = fields?.transactions || [];

  return (
    <div className="mt-8 bg-white shadow-2xl rounded-xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-5 flex items-center gap-3">
        <CreditCard className="w-6 h-6" />
        <h2 className="text-xl font-semibold">Bank: {bank}</h2>
      </div>

      {/* Summary Table */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <CalendarDays className="w-5 h-5 text-indigo-600" />
          Statement Summary
        </h3>

        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table className="min-w-full text-sm text-gray-700 bg-white">
            <tbody>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold w-1/3 text-gray-600">Last 4 Digits</td>
                <td className="px-4 py-2">{fields.last4 || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Statement Date</td>
                <td className="px-4 py-2">{fields.statement_date || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Billing Cycle Start</td>
                <td className="px-4 py-2">{fields.billing_cycle_start || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Billing Cycle End</td>
                <td className="px-4 py-2">{fields.billing_cycle_end || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Payment Due Date</td>
                <td className="px-4 py-2">{fields.payment_due_date || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Total Balance</td>
                <td className="px-4 py-2 text-green-700 font-semibold">{fields.total_balance || "-"}</td>
              </tr>
              <tr className="odd:bg-gray-50 even:bg-white">
                <td className="px-4 py-2 font-semibold text-gray-600">Minimum Due</td>
                <td className="px-4 py-2 text-red-700 font-semibold">{fields.minimum_due || "-"}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="p-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Banknote className="w-5 h-5 text-green-600" />
          Transactions
        </h3>

        {transactions.length === 0 ? (
          <p className="text-gray-500 text-sm">No transactions found.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-indigo-50">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold text-gray-700">Date</th>
                  <th className="px-4 py-2 text-left font-semibold text-gray-700">Description</th>
                  <th className="px-4 py-2 text-right font-semibold text-gray-700">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {transactions.map((tx, index) => (
                  <tr key={index} className="hover:bg-indigo-50 transition">
                    <td className="px-4 py-2 text-gray-800">{tx.date || "-"}</td>
                    <td className="px-4 py-2 text-gray-600">{tx.description || "-"}</td>
                    <td className="px-4 py-2 text-right text-gray-900 font-medium">
                      ₹{tx.amount || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

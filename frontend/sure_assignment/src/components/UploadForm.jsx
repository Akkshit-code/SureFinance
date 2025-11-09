import React, { useState } from "react";
import axios from "axios";
import ResultCard from "./ResultCard";
import { Loader2 } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setResult(null);
  };

  const upload = async () => {
    if (!file) return setError("Please select a PDF file first.");
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(`${API_BASE}/parse`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
    } catch (err) {
      console.error("Upload error:", err);
      setError(
        err.response?.data?.error ||
          "⚠️ Unable to reach backend. Check if FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const clear = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-3xl bg-white shadow-xl rounded-2xl border border-gray-200 p-10 space-y-6">
      {/* Title */}
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Credit Card Statement Parser
        </h1>
        <p className="text-gray-600 mt-2">
          Upload your PDF statement (Kotak, Axis, HDFC, SBI , ICICI) and extract key details.
        </p>
      </header>

      {/* Upload Controls */}
      <section className="flex flex-col items-center justify-center gap-4 pd-10">
        {/* Centered File Input */}
        <div className="flex justify-center w-full">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="block w-auto text-sm text-gray-700 border border-gray-300 rounded-lg cursor-pointer
              file:mr-4 file:py-2 file:px-6
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-indigo-600 file:text-white
              hover:file:bg-indigo-700 transition
              shadow-sm"
          />
        </div>

        {/* Buttons */}
        <div className="flex flex-row justify-center gap-4 mt-20">
          <button
            onClick={upload}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-6 py-2 rounded-lg 
            bg-gradient-to-r from-green-500 to-emerald-600 text-white 
            hover:from-green-600 hover:to-emerald-700 
            font-semibold shadow-md transition disabled:opacity-60"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin w-4 h-4" />
                Parsing...
              </>
            ) : (
              "Upload & Parse"
            )}
          </button>

          <button
            onClick={clear}
            className="px-6 py-2 rounded-lg bg-gradient-to-r from-gray-200 to-gray-300 
            hover:from-gray-300 hover:to-gray-400 text-gray-800 font-semibold shadow-sm transition"
          >
            Clear
          </button>
        </div>
      </section>

      {/* File Name */}
      {file && (
        <p className="text-center text-gray-500 text-sm">
          Selected file:{" "}
          <span className="font-medium text-gray-700">{file.name}</span>
        </p>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-center font-medium">
          {error}
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center gap-3">
            <Loader2 className="animate-spin w-8 h-8 text-indigo-600" />
            <p className="text-gray-700 font-semibold">Parsing your statement...</p>
          </div>
        </div>
      )}

      {/* Parsed Result */}
      {result && result.success && (
        <div className="mt-8">
          <ResultCard bank={result.bank} fields={result.fields} />
        </div>
      )}

      {/* Footer */}
      {/* <footer className="text-center text-sm text-gray-500 pt-4 border-t border-gray-100">
        Built with ❤️ using{" "}
        <span className="font-semibold text-indigo-600">React</span>,{" "}
        <span className="font-semibold text-indigo-600">TailwindCSS</span> &{" "}
        <span className="font-semibold text-indigo-600">FastAPI</span>
      </footer> */}
    </div>
  );
}

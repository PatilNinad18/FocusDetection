import React, { useState, useEffect } from "react";

function TimerCircle() {
  const [selectedTime, setSelectedTime] = useState(25);
  const [timeLeft, setTimeLeft] = useState(selectedTime * 60);
  const [isRunning, setIsRunning] = useState(false);
  const [videoActive, setVideoActive] = useState(false);

  // 🧠 Live focus data
  const [focusScore, setFocusScore] = useState(100);
  const [distractions, setDistractions] = useState(0);

  // Update time when duration changes
  useEffect(() => {
    setTimeLeft(selectedTime * 60);
  }, [selectedTime]);

  // Countdown logic
  useEffect(() => {
    let timer;
    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [isRunning, timeLeft]);

  const minutes = String(Math.floor(timeLeft / 60)).padStart(2, "0");
  const seconds = String(timeLeft % 60).padStart(2, "0");

  // Reset
  const handleReset = () => {
    setTimeLeft(selectedTime * 60);
    setIsRunning(false);
    setVideoActive(false);
    fetch("http://127.0.0.1:8000/stop_session", { method: "POST" });
  };

  // Start/Stop focus session
  const handleStartStop = async () => {
    if (!isRunning) {
      console.log("🟢 Starting focus session...");
      const res = await fetch("http://127.0.0.1:8000/start_session", { method: "POST" });
      const data = await res.json();
      console.log("✅ Backend response:", data);
      if (data.status === "success") setVideoActive(true);
    } else {
      console.log("🔴 Stopping focus session...");
      const res = await fetch("http://127.0.0.1:8000/stop_session", { method: "POST" });
      const data = await res.json();
      console.log("🛑 Backend stop:", data);
      setVideoActive(false);
    }
    setIsRunning(!isRunning);
  };

  // 🔁 Poll backend for live focus data
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/focus_data");
        const data = await res.json();
        console.log("📊 Focus Data:", data);
        setFocusScore(data.focus_score ?? 0);
        setDistractions(data.distractions ?? 0);
      } catch (err) {
        console.error("⚠️ Focus data fetch failed:", err);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Circle progress
  const progress = ((selectedTime * 60 - timeLeft) / (selectedTime * 60)) * 100;
  const radius = 240;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center mt-20 select-none">
      {/* Two-column layout */}
      <div className="flex flex-col lg:flex-row items-center justify-center gap-12">
        
        {/* LEFT: Timer Circle */}
        <div className="relative w-[550px] h-[450px] overflow-hidden">
          <svg width="550" height="550" viewBox="0 0 600 600" className="absolute top-[-50px] left-0">
            <defs>
              <linearGradient id="focusGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#22c55e" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>

            <circle cx="300" cy="300" r={radius} stroke="rgba(255,255,255,0.2)" strokeWidth="10" fill="none" />
            <circle
              cx="300"
              cy="300"
              r={radius}
              stroke="url(#focusGradient)"
              strokeWidth="10"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              transform="rotate(-90 300 300)"
              style={{ transition: "stroke-dashoffset 0.5s linear" }}
            />
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center mt-8">
            <h1 className="text-[130px] font-bold text-white leading-none drop-shadow-lg">
              {minutes}:{seconds}
            </h1>
            <p className="text-2xl text-gray-200 mt-4 font-light text-center">
              Time to focus.
            </p>
          </div>
        </div>

        {/* RIGHT: Live Camera Stream + Overlay */}
        {videoActive && (
          <div className="relative w-[640px] h-auto border border-white/20 rounded-xl overflow-hidden">
            <img
              src={`http://127.0.0.1:8000/video_feed?cacheBust=${Date.now()}`}
              alt="Live focus stream"
              className="w-full"
            />

            {/* Overlay for focus score */}
            <div className="absolute top-3 left-3 bg-black/50 text-white px-4 py-2 rounded-lg text-sm backdrop-blur-sm">
              <span className="text-green-400 font-semibold">Focus:</span> {focusScore}%
            </div>

            {/* Overlay for distractions */}
            <div className="absolute top-3 right-3 bg-black/50 text-white px-4 py-2 rounded-lg text-sm backdrop-blur-sm">
              <span className="text-red-400 font-semibold">Distractions:</span> {distractions}
            </div>
          </div>
        )}
      </div>

      {/* Duration Selector */}
      {!isRunning && (
        <div className="flex gap-4 mt-10">
          {[15, 25, 45, 60].map((option) => (
            <button
              key={option}
              onClick={() => setSelectedTime(option)}
              className={`px-6 py-2 rounded-full text-lg border border-white/20 backdrop-blur-md transition-all duration-300 ${
                selectedTime === option
                  ? "bg-green-500/30 text-white border-green-400/50"
                  : "bg-white/10 text-gray-300 hover:bg-white/20"
              }`}
            >
              {option}m
            </button>
          ))}
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex items-center gap-5 mt-6">
        <button
          onClick={handleStartStop}
          className={`px-10 py-3 text-lg rounded-full border border-white/30 backdrop-blur-md transition-all duration-300 ${
            isRunning
              ? "bg-white/20 hover:bg-white/30 text-white"
              : "bg-green-500/20 hover:bg-green-500/30 text-green-400"
          }`}
        >
          {isRunning ? "Pause" : "Start"}
        </button>

        <button
          onClick={handleReset}
          className="px-10 py-3 text-lg rounded-full border border-white/30 backdrop-blur-md text-white hover:bg-white/20 transition-all duration-300"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

export default TimerCircle;

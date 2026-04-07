"use client";
import React from "react";

interface CircleTimerProps {
  duration: number;
  timeLeft: number;
  isPaused: boolean;
  size?: number;
}

export default function CircleTimer({ duration, timeLeft, isPaused, size = 48 }: CircleTimerProps) {
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = timeLeft / duration;
  const strokeDashoffset = circumference * (1 - progress);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: "rotate(-90deg)" }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#EBEBEB"
          strokeWidth="3"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={isPaused ? "#FFB347" : "#FF6B35"}
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: "stroke-dashoffset 1s linear, stroke 0.3s ease" }}
        />
      </svg>
      <span
        className="absolute inset-0 flex items-center justify-center font-display font-bold text-fg"
        style={{ fontSize: size * 0.25 }}
      >
        {isPaused ? "⏸" : timeLeft}
      </span>
    </div>
  );
}

import React from "react";
import { Calendar } from "react-feather";

function CalendarDisplay() {
  const today = new Date();

  const day = today.toLocaleDateString("en-US", { weekday: "short" });
  const date = today.getDate();
  const month = today.toLocaleDateString("en-US", { month: "short" });

  const formatted = `${day}, ${date} ${month}`;

  return (
    <div className="flex items-center gap-2 text-gray-300 text-sm">
      <Calendar className="text-white" size={15} />
      <span>{formatted}</span>
    </div>
  );
}

export default CalendarDisplay;
    
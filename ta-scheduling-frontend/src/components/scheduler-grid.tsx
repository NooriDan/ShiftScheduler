import { useTimetableContext } from "@/context/app-context";
import { Shift } from "@/models/domain";
import React from "react";

export const time_strings = [
    "8:30 AM",
    "9:30 AM",
    "10:30 AM",
    "11:30 AM",
    "12:30 PM",
    "1:30 PM",
    "2:30 PM",
    "3:30 PM",
    "4:30 PM",
    "5:30 PM",
    "6:30 PM",
    "7:30 PM",
    "8:30 PM",
    "9:30 PM",
    "10:30 PM"
];

function TimeBlock({ time }: { time: string }) {
    return (<div
        className="h-16 pl-2 flex flex-row items-center justify-center text-center text-sm"
    >
        {time} <hr className="h-[0.125rem] flex-1 bg-black" />
    </div>)
}

// Shift placement calculation
function calculateShiftPosition(startTime: string, endTime: string) {
    const convertTimeToIndex = (time: string) => {
        const [hour, minute, period] = time.match(/(\d+):(\d+)\s*(AM|PM)/i)!.slice(1);
        let hour24 = parseInt(hour) % 12 + (period === "PM" ? 12 : 0);
        const minutes = parseInt(minute);
        const totalMinutes = hour24 * 60 + minutes;
        return totalMinutes;
    };

    const slotDuration = 60; // Each time slot is 1 hour
    const startMinutes = convertTimeToIndex(startTime);
    const endMinutes = convertTimeToIndex(endTime);

    const startOffset = (startMinutes - 510) / slotDuration; // Offset in slots (8:30 AM = 510 minutes)
    const duration = (endMinutes - startMinutes) / slotDuration;

    return { startOffset, duration };
};

function ShiftBlock({ shift }: { shift: Shift }) {
    const { startOffset, duration } = calculateShiftPosition(
        shift.start_time,
        shift.end_time
    );
    const { state } = useTimetableContext()
    // TODO: later when working with API, replace this with shift assignments and modify it to show whether it is desired, undesired, neutral, or unavailable
    const assignments = state.shift_assignments.filter(assignment => assignment.shift.id === shift.id).map(assignment => assignment.assigned_ta.name)

    return (
        <div
            className={`absolute w-full left-0 bg-blue-500 text-white rounded shadow-md p-1`}
            style={{
                top: `${startOffset * 4 + 2}rem`, // Adjusted by 4rem per slot
                height: `${duration * 4}rem`,
            }}
        >
            <div>{shift.series}</div>
            <div>Required TAs: {shift.required_tas}</div>

            {assignments.map((name, idx) => <div key={idx}>{name}</div>)}
        </div>
    );

}

function DayBlock({ day }: { day: string }) {
    const { state } = useTimetableContext()

    // Example shifts data
    return (<div className="col-span-1 border-r border-black relative">
        {/* Day header */}
        <div className="h-8 bg-gray-300 flex items-center justify-center border-b border-black font-semibold">
            {day}
        </div>

        {/* Time slots for the day */}
        {time_strings.map((_, idx) => (
            <div key={idx} className="h-16 border-b border-black relative"></div>
        ))}

        {/* Render shifts for the current day */}
        {state.shifts
            .filter((shift) => shift.day_of_week === day)
            .map((shift, idx) => <ShiftBlock key={idx} shift={shift} />)}
    </div>)
}

export default function Scheduler() {
    const timeSlots = time_strings
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];


    return (
        <div className="w-full h-full overflow-auto p-4">
            {/* Table structure */}
            <div className="grid grid-cols-[100px_repeat(5,_1fr)] gap-0 border">
                {/* Time Column */}
                <div className="bg-gray-200 border-r border-black">
                    {timeSlots.map((time, idx) => <TimeBlock key={idx} time={time} />)}
                </div>

                {/* Weekdays */}
                {days.map((day, idx) => <DayBlock key={idx} day={day} />)}
            </div>
        </div>
    );
};
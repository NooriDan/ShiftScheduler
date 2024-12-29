import { useTimetableContext } from "@/context/app-context"
import { Shift, ShiftAssignment, TA } from "@/models/domain"

function TABlock({ ta }: { ta: TA }) {
    return (<div className="bg-gray-200">{ta.name} (ID: {ta.id}) (requires: {ta.required_shifts})</div>);
}

function ShiftBlock({ shift }: { shift: Shift }) {
    return (<div className="bg-gray-200">{shift.series} {shift.day_of_week} {shift.start_time} requires {shift.required_tas}</div>);
}

function ShiftAssignmentBlock({ ta, shift }: { ta: TA, shift: Shift }) {
    const { state } = useTimetableContext()
    const shift_assignments = state.shift_assignments
    const assignment = shift_assignments.find(assignment => assignment.assigned_ta.id === ta.id && assignment.shift.id === shift.id) as ShiftAssignment

    if (assignment) {
        const desiredness = ta.desired.includes(shift) ? "desired" : ta.undesired.includes(shift) ? "undesired" : ta.unavailable.includes(shift) ? "unavailable" : "neutral"

        return (<div>{ta.name} {desiredness}</div>)
    } else {
        return (<div></div>)
    }
}

function ShiftRow({ shift }: { shift: Shift }) {
    const { state } = useTimetableContext()
    const tas = state.tas

    return (<div>
        <ShiftBlock shift={shift} />
        {tas.map(ta => <ShiftAssignmentBlock key={ta.id} ta={ta} shift={shift} />)}
    </div>)
}

export default function ShiftView() {
    const { state } = useTimetableContext()
    const shifts = state.shifts
    const tas = state.tas

    return (<div>
        <div className="font-bold">Shifts View</div>

        <div className={`grid grid-cols-[repeat(${tas.length + 1},minmax(0,1fr))] grid-rows-[repeat(${shifts.length + 1},minmax(0,1fr))] gap-2`}>
            {/* Column Headers */}
            <div className="bg-gray-200"></div>
            {tas.map(ta => <TABlock key={ta.id} ta={ta} />)}

            {/* Rows */}
            {shifts.map(shift => <ShiftRow key={shift.id} shift={shift} />)}
        </div>

    </div>)
}
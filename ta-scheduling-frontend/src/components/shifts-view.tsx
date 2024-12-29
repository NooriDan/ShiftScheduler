import { useTimetableContext } from "@/context/app-context"
import { Shift, ShiftAssignment, TA } from "@/models/domain"

function TABlock({ ta, index }: { ta: TA, index: number }) {
    return (<div className={`bg-gray-200 row-start-1 col-start-${index + 2}`}>{ta.name} (ID: {ta.id}) (requires: {ta.required_shifts})</div>);
}

function ShiftBlock({ shift, row }: { shift: Shift, row: number }) {
    return (<div className={`bg-gray-200 col-start-1 row-start-${row + 2}`}>{shift.series} {shift.day_of_week} {shift.start_time} requires {shift.required_tas}</div>);
}

function ShiftAssignmentBlock({ ta, shift, row, col }: { ta: TA, shift: Shift, row: number, col: number }) {
    const { state } = useTimetableContext()
    const shift_assignments = state.shift_assignments
    const assignment = shift_assignments.find(assignment => assignment.assigned_ta && assignment.assigned_ta.id === ta.id && assignment.shift.id === shift.id) as ShiftAssignment

    if (assignment) {
        const desiredness = ta.desired.includes(shift) ? "desired" : ta.undesired.includes(shift) ? "undesired" : ta.unavailable.includes(shift) ? "unavailable" : "neutral"

        return (<div className={`col-start-${col + 2} row-start-${row + 2}`}>{ta.name} {desiredness}</div>)
    } else {
        return (<div className={`col-start-${col + 2} row-start-${row + 2}`}></div>)
    }
}

function ShiftRow({ shift, index }: { shift: Shift, index: number }) {
    const { state } = useTimetableContext()
    const tas = state.tas

    return (<>
        <ShiftBlock shift={shift} row={index} />
        {tas.map((ta, col) => <ShiftAssignmentBlock key={ta.id} ta={ta} shift={shift} row={index} col={col} />)}
    </>)
}

export default function ShiftView() {
    const { state } = useTimetableContext()
    const shifts = state.shifts
    const tas = state.tas

    return (<div>
        <div className="font-bold">Shifts View</div>

        <div className={`grid grid-cols-[repeat(${tas.length + 1},minmax(0,1fr))] grid-rows-[repeat(${shifts.length + 1},minmax(0,1fr))] gap-2`}>
            {/* Column Headers */}
            <div className="bg-gray-200 row-start-1 col-start-1"></div>
            {tas.map((ta, index) => <TABlock key={ta.id} ta={ta} index={index} />)}

            {/* Rows */}
            {shifts.map((shift, index) => <ShiftRow key={shift.id} shift={shift} index={index} />)}
        </div>

    </div>)
}
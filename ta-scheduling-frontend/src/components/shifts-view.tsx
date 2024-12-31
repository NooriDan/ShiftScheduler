import { useTimetableContext } from "@/context/app-context"
import { get_status_for_shift, Shift, ShiftAssignment, TA } from "@/models/domain"

function TABlock({ ta }: { ta: TA }) {
    return <th key={ta.id} className="p-2 border-x">{ta.name} - {ta.id}</th>
}

function ShiftAssignmentBlock({ ta, shift }: { ta: TA, shift: Shift }) {
    const { state } = useTimetableContext()
    const shift_assignments = state.shiftAssignments
    const assignment = shift_assignments.find(assignment => assignment.assignedTa && assignment.assignedTa.id === ta.id && assignment.shift.id === shift.id) as ShiftAssignment

    if (assignment) {
        const desiredness = get_status_for_shift(ta, shift)

        return (<td key={ta.id} className="p-2 border-x">{ta.name} - {desiredness}</td>)
    } else {
        return (<td key={ta.id} className="p-2 border-x"></td>)
    }
}

function ShiftRow({ shift }: { shift: Shift }) {
    const { state } = useTimetableContext()
    const tas = state.tas

    return (<tr key={shift.id} className="border">
        <td className="p-2 border-x bg-gray-100 font-bold">{shift.series}</td>
        {tas.map(ta => <ShiftAssignmentBlock key={ta.id} ta={ta} shift={shift} />)}
    </tr>)
}

export default function ShiftView() {
    const { state } = useTimetableContext()
    const shifts = state.shifts
    const tas = state.tas

    return (<div>
        <div className="font-bold">Shifts View</div>


        <table className="table-auto">
            <thead>
                <tr className="border bg-gray-100">
                    <th className="p-2 border-x">Shift</th>
                    {tas.map(ta => <TABlock key={ta.id} ta={ta} />)}
                </tr>
            </thead>
            <tbody>
                {shifts.map(shift => <ShiftRow key={shift.id} shift={shift} />)}
            </tbody>
        </table>

    </div>)
}
import { useTimetableContext } from "@/context/app-context"


export default function TAView() {
    const { state } = useTimetableContext()

    return (<div>
        <div className="font-bold">TA View</div>

        <table className="table-auto border-b">
            <thead>
                <tr className="border bg-gray-100">
                    <th className="p-2 border-x">TA</th>
                    <th className="p-2 border-x">Desired Shifts</th>
                    <th className="p-2 border-x">Undesired Shifts</th>
                    <th className="p-2 border-x">Unavailable Shifts</th>
                    <th className="p-2 border-x">Assigned Shifts</th>
                </tr>
            </thead>
            <tbody>
                {
                    state.tas.map(ta => <tr key={ta.id} className="border">
                        <td className="p-2 border-x">{ta.name} (ID: {ta.id}) (requires: {ta.requiredShifts})</td>
                        <td className="p-2 border-x">{ta.desired.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2 border-x">{ta.undesired.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2 border-x">{ta.unavailable.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2 border-x">{state.shiftAssignments.filter(assignment => assignment.assignedTa && assignment.assignedTa.id === ta.id).map(assignment => assignment.shift.series).join(", ")}</td>
                    </tr>)
                }
            </tbody>
        </table>
    </div>)
}
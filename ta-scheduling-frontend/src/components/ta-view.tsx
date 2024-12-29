import { useTimetableContext } from "@/context/app-context"


export default function TAView() {
    const { state } = useTimetableContext()

    return (<div>
        <div className="font-bold">TA View</div>

        <table className="table-auto">
            <thead>
                <tr className="border bg-gray-100">
                    <th className="p-2">TA</th>
                    <th className="p-2">Desired Shifts</th>
                    <th className="p-2">Undesired Shifts</th>
                    <th className="p-2">Unavailable Shifts</th>
                    <th className="p-2">Assigned Shifts</th>
                </tr>
            </thead>
            <tbody>
                {
                    state.tas.map(ta => <tr key={ta.id} className="border">
                        <td className="p-2">{ta.name} (ID: {ta.id}) (requires: {ta.required_shifts})</td>
                        <td className="p-2">{ta.desired.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2">{ta.undesired.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2">{ta.unavailable.map(shift => shift.series).join(", ")}</td>
                        <td className="p-2">{state.shift_assignments.filter(assignment => assignment.assigned_ta && assignment.assigned_ta.id === ta.id).map(assignment => assignment.shift.series).join(", ")}</td>
                    </tr>)
                }
            </tbody>
        </table>
    </div>)
}
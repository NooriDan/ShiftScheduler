import { useTimetableContext } from "@/context/app-context"
import { Shift, TA } from "@/models/domain"
import { useReducer } from "react"
import AvailabilityChooser, { reducer } from "./availability-chooser"

export default function TAForm({ ta, action }: { ta?: TA, action: (ta: TA) => void }) {
    const { state } = useTimetableContext()
    // States for desired, undesired, and unavailable shifts
    const [desiredShifts, desiredShiftsDispatch] = useReducer<Shift[], any>(reducer, ta ? ta.desired : [])
    const [undesiredShifts, undesiredShiftsDispatch] = useReducer<Shift[], any>(reducer, ta ? ta.undesired : [])
    const [unavailableShifts, unavailableShiftsDispatch] = useReducer<Shift[], any>(reducer, ta ? ta.unavailable : [])
    // Get the shifts from the context
    const shifts = state.shifts
    const available = shifts.filter(shift => !desiredShifts.includes(shift) && !undesiredShifts.includes(shift) && !unavailableShifts.includes(shift))

    // Submit the form
    const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        const formData = new FormData(e.currentTarget)

        const id = formData.get("id") as string
        const name = formData.get("name") as string
        const required_shifts = parseInt(formData.get("required_shifts") as string)
        const is_grad_student = formData.get("is_grad_student") as string

        if (state.tas.find(ta => ta.id === id)) {
            alert("TA already exists")
            return
        }

        const ta = new TA(id, name, required_shifts)
        ta.isGradStudent = is_grad_student === "on"

        // Add the desired shifts
        ta.desired = desiredShifts.map(id => shifts.find(shift => shift === id) as Shift)
        // Add the undesired shifts
        ta.undesired = undesiredShifts.map(id => shifts.find(shift => shift === id) as Shift)
        // Add the unavailable shifts
        ta.unavailable = unavailableShifts.map(id => shifts.find(shift => shift === id) as Shift)

        action(ta)
    }

    return (<div>
        <div className="font-bold">TA Form</div>
        <form onSubmit={onSubmit}>
            <div>
                <label>Mac ID: </label>
                <input name="id" type="text" defaultValue={ta && ta.id} placeholder="Mac ID" className="border rounded p-1" required />
            </div>

            <div>
                <label>Name: </label>
                <input name="name" type="text" defaultValue={ta && ta.name} placeholder="Name" className="border rounded p-1" required />
            </div>

            <div>
                <label>Required Shifts: </label>
                <input name="required_shifts" type="number" defaultValue={ta && ta.requiredShifts} placeholder="Required Shifts" className="border rounded p-1" required />
            </div>

            <div>
                <label>Is Grad Student: </label>
                <input name="is_grad_student" type="checkbox" defaultValue={ta && ta.isGradStudent ? "on" : "off"} className="border rounded p-1" />
            </div>

            <div>
                <div>Desired Shifts:</div>
                <AvailabilityChooser shifts={desiredShifts} dispatch={desiredShiftsDispatch} available={available} name="desired" />
            </div>

            <div>
                <div>Undesired Shifts:</div>
                <AvailabilityChooser shifts={undesiredShifts} dispatch={undesiredShiftsDispatch} available={available} name="undesired" />
            </div>

            <div>
                <div>Unavailable Shifts:</div>
                <AvailabilityChooser shifts={unavailableShifts} dispatch={unavailableShiftsDispatch} available={available} name="unavailable" />
            </div>

            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Add TA</button>
        </form>
    </div>)
}

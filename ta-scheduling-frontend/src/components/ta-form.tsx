import { addTA } from "@/context/app-reducers"
import { useTimetableContext } from "@/context/app-context"
import { Shift, TA } from "@/models/domain"
import { useReducer } from "react"
import DesiredChooser, { reducer } from "./desired-chooser"

export default function TAForm() {
    const { state, dispatch } = useTimetableContext()
    // States for desired, undesired, and unavailable shifts
    const [desiredShifts, desiredShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    const [undesiredShifts, undesiredShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    const [unavailableShifts, unavailableShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    // Get the shifts from the context
    const shifts = state.shifts
    const available = shifts.filter(shift => !desiredShifts.includes(shift) && !undesiredShifts.includes(shift) && !unavailableShifts.includes(shift))

    // Submit the form
    const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        const formData = new FormData(e.currentTarget)

        const name = formData.get("name") as string
        const required_shifts = parseInt(formData.get("required_shifts") as string)
        const is_grad_student = formData.get("is_grad_student") as string

        const ta = new TA("", name, required_shifts)
        ta.is_grad_student = is_grad_student === "on"

        // Add the desired shifts
        ta.desired = desiredShifts.map(id => shifts.find(shift => shift === id) as Shift)
        // Add the undesired shifts
        ta.undesired = undesiredShifts.map(id => shifts.find(shift => shift === id) as Shift)
        // Add the unavailable shifts
        ta.unavailable = unavailableShifts.map(id => shifts.find(shift => shift === id) as Shift)

        // Add the TA to the context
        dispatch(addTA(ta))
    }

    return (<div>
        <div className="font-bold">TA Form</div>
        <form onSubmit={onSubmit}>
            <div>
                <label>Name: </label>
                <input name="name" type="text" placeholder="Name" className="border rounded p-1" required />
            </div>

            <div>
                <label>Required Shifts: </label>
                <input name="required_shifts" type="number" placeholder="Required Shifts" className="border rounded p-1" required />
            </div>

            <div>
                <label>Is Grad Student: </label>
                <input name="is_grad_student" type="checkbox" className="border rounded p-1" required />
            </div>

            <div>
                <div>Desired Shifts:</div>
                <DesiredChooser shifts={desiredShifts} dispatch={desiredShiftsDispatch} available={available} />
            </div>

            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Add TA</button>
        </form>
    </div>)
}
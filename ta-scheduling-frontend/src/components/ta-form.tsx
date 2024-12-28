import { addShift, addTA } from "@/context/app-reducers"
import { time_strings } from "./scheduler-grid"
import { useTimetableContext } from "@/context/app-context"
import { DayOfWeek, Shift, TA } from "@/models/domain"
import { useReducer } from "react"
import internal from "stream"

const reducer = (state: Shift[], action: any) => {
    switch (action.type) {
        case "add":
            return [...state, action.payload]
        case "remove":
            return state.filter(item => item !== action.payload)
        case "set_index":
            state[action.payload.index] = action.payload.shift
            return [...state]
        default:
            return state
    }
}

// function ShiftItem({ shift, onSet, onRemove, available }: { shift: Shift, available: Shift[], onSet: (index: number, shift: Shift) => void, onRemove: (shift: Shift) => void }) {
//     return (
//         <div>
//             <select>
//                 {available.map((shift, index) => <option key={shift.id} value={shift.id} onClick={() => onSet(index, shift)}>
//                     {shift.alias} {shift.day_of_week} {shift.start_time} - {shift.end_time}
//                 </option>)}
//             </select>
//             <button onClick={() => onRemove(shift)}>Remove</button>
//         </div>
//     )
// }

export default function TAForm() {
    const { state, dispatch } = useTimetableContext()
    // States for desired, undesired, and unavailable shifts
    const [desiredShifts, desiredShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    const [undesiredShifts, undesiredShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    const [unavailableShifts, unavailableShiftsDispatch] = useReducer<Shift[], any>(reducer, [])
    // Get the shifts from the context
    const shifts = state.shifts
    // Get available shifts
    // const availableShifts = shifts.filter(shift => !desiredShifts.includes(shift) && !undesiredShifts.includes(shift) && !unavailableShifts.includes(shift))

    // // Add a shift to the desired shifts
    // const addDesiredShift = () => {
    //     desiredShiftsDispatch({ type: "add", payload: availableShifts[0] })
    // }

    // // Remove a shift from the desired shifts
    // const removeDesiredShift = (shift: Shift) => {
    //     desiredShiftsDispatch({ type: "remove", payload: shift.id })
    // }

    // // Set a shift from the desired shifts
    // const setDesiredShift = (index: number, shift: Shift) => {
    //     desiredShiftsDispatch({ type: "set_index", payload: { index, shift } })
    // }

    // // Add a shift to the undesired shifts
    // const addUndesiredShift = () => {
    //     undesiredShiftsDispatch({ type: "add", payload: availableShifts[0] })
    // }

    // // Remove a shift from the undesired shifts
    // const removeUndesiredShift = (shift: Shift) => {
    //     undesiredShiftsDispatch({ type: "remove", payload: shift.id })
    // }

    // // Set a shift from the undesired shifts
    // const setUndesiredShift = (index: number, shift: Shift) => {
    //     undesiredShiftsDispatch({ type: "set_index", payload: { index, shift } })
    // }

    // // Add a shift to the unavailable shifts
    // const addUnavailableShift = () => {
    //     unavailableShiftsDispatch({ type: "add", payload: availableShifts[0] })
    // }

    // // Remove a shift from the unavailable shifts
    // const removeUnavailableShift = (shift: Shift) => {
    //     unavailableShiftsDispatch({ type: "remove", payload: shift.id })
    // }

    // // Set a shift from the unavailable shifts
    // const setUnavailableShift = (index: number, shift: Shift) => {
    //     unavailableShiftsDispatch({ type: "set_index", payload: { index, shift } })
    // }

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
{/* 
            <div>
                <label>Desired Shifts: </label>
                <button onClick={addDesiredShift}>Add Desired</button>

                {desiredShifts.map((id, index) => <ShiftItem key={id.id} shift={id} onSet={setDesiredShift} onRemove={removeDesiredShift} available={availableShifts} />)}
            </div>

            <div>
                <label>Undesired Shifts: </label>
                <button onClick={addUndesiredShift}>Add Undesired</button>

                {undesiredShifts.map((id, index) => <ShiftItem key={id.id} shift={id} onSet={setUndesiredShift} onRemove={removeUndesiredShift} available={availableShifts} />)}

            </div>

            <div>
                <label>Unavailable Shifts: </label>
                <button onClick={addUndesiredShift}>Add Unavailable</button>

                {unavailableShifts.map((id, index) => <ShiftItem key={id.id} shift={id} onSet={setUnavailableShift} onRemove={removeUnavailableShift} available={availableShifts} />)}

            </div> */}

            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Add TA</button>
        </form>
    </div>)
}

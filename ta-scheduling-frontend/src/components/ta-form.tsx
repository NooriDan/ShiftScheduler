import { addShift, addTA } from "@/context/app-reducers"
import { time_strings } from "./scheduler-grid"
import { useTimetableContext } from "@/context/app-context"
import { DayOfWeek, Shift, TA } from "@/models/domain"

export default function TAForm() {
    const { dispatch } = useTimetableContext()

    const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        const formData = new FormData(e.currentTarget)

        const name = formData.get("name") as string
        const required_shifts = parseInt(formData.get("required_shifts") as string)
        const is_grad_student = formData.get("is_grad_student") as string

        const ta = new TA("", name, required_shifts)
        ta.is_grad_student = is_grad_student === "on"
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

            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Add TA</button>
        </form>
    </div>)
}

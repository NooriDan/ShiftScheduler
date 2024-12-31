import { addShift } from "@/context/app-reducers"
import { time_strings } from "./scheduler-grid"
import { useTimetableContext } from "@/context/app-context"
import { DayOfWeek, Shift } from "@/models/domain"
import { convertEuropeanToAmericanTime } from "@/models/time-utils"

export default function ShiftForm({ action }: { action: (ta: Shift) => void }) {
    const { state } = useTimetableContext()

    const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        const formData = new FormData(e.currentTarget)

        const series = formData.get("series") as string
        const required_tas = parseInt(formData.get("required_tas") as string)
        const day_of_week = formData.get("day_of_week") as DayOfWeek
        const start_time = formData.get("start_time") as string
        const end_time = formData.get("end_time") as string

        console.log(start_time)
        console.log(end_time)

        const shift = new Shift("", series, day_of_week, start_time, end_time, required_tas, "CS 100 Lab")

        const duplicate = state.shifts.find(s => s.series === shift.series && s.dayOfWeek === shift.dayOfWeek && s.startTime === shift.startTime && s.endTime === shift.endTime)

        if (duplicate) {
            alert("Shift already exists")
            return
        }

        action(shift)
    }

    return (<div>
        <div className="font-bold">Shift Form</div>
        <form onSubmit={onSubmit}>
            <div>
                <label>Series: </label>
                <input name="series" type="text" placeholder="Series" className="border rounded p-1" required />
            </div>

            <div>
                <label>Required TAs: </label>
                <input name="required_tas" type="number" placeholder="Required TAs" className="border rounded p-1" required />
            </div>

            <div>
                <label>Day of Week: </label>
                <select name="day_of_week" className="border rounded p-1" required>
                    {
                        Object.values(DayOfWeek).map(day => <option key={day}>{day}</option>)
                    }
                </select>
            </div>

            <div>
                <label>Start Time: </label>
                <select name="start_time" className="border rounded p-1" required>
                    {time_strings.map(time => <option key={time} value={time}>{convertEuropeanToAmericanTime(time)}</option>)}
                </select>
            </div>

            <div>
                <label>End Time: </label>
                <select name="end_time" className="border rounded p-1" required>
                    {time_strings.map(time => <option key={time} value={time}>{convertEuropeanToAmericanTime(time)}</option>)}
                </select>
            </div>
            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Add Shift</button>
        </form>
    </div>)
}

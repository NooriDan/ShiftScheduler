import SchedulerGrid, { time_strings } from "@/components/scheduler-grid";
import { useTimetableContext } from "@/context/app-context";
import { addShift } from "@/context/app-reducers";
import { DayOfWeek, Shift, TA } from "@/models/domain";
import { useState } from "react";

function ShiftDisplay({ shift }: { shift: Shift }) {
    return <div>{shift.alias} - {shift.day_of_week} {shift.start_time}-{shift.end_time}</div>
}

function TADisplay({ ta }: { ta: TA }) {
    return <div>{ta.name} {ta.is_grad_student ? "Grad" : "Undergrad"} - Required Shifts: {ta.required_shifts} </div>
}

type FormState = "Hidden" | "Shift" | "TA";


function ShiftForm() {
    const { dispatch } = useTimetableContext()

    const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        const formData = new FormData(e.currentTarget)

        const series = formData.get("series") as string
        const required_tas = parseInt(formData.get("required_tas") as string)
        const day_of_week = formData.get("day_of_week") as DayOfWeek
        const start_time = formData.get("start_time") as string
        const end_time = formData.get("end_time") as string

        const shift = new Shift("", series, day_of_week, start_time, end_time, required_tas, "CS 100 Lab")
        dispatch(addShift(shift))
    }

    return (<div>
        <div className="font-bold">Shift Form</div>
        <form onSubmit={onSubmit}>
            <div>
                <label>Series: </label>
                <input name="series" type="text" placeholder="Series" className="border rounded p-1" />
            </div>

            <div>
                <label>Required TAs: </label>
                <input name="required_tas" type="number" placeholder="Required TAs" className="border rounded p-1" />
            </div>

            <div>
                <label>Day of Week: </label>
                <select name="day_of_week" className="border rounded p-1">
                    {
                        Object.values(DayOfWeek).map(day => <option key={day}>{day}</option>)
                    }
                </select>
            </div>

            <div>
                <label>Start Time: </label>
                <select name="start_time" className="border rounded p-1">
                    {time_strings.map(time => <option key={time}>{time}</option>)}
                </select>
            </div>

            <div>
                <label>End Time: </label>
                <select name="end_time" className="border rounded p-1">
                    {time_strings.map(time => <option key={time}>{time}</option>)}
                </select>
            </div>
            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400">Add Shift</button>
        </form>
    </div>)
}

function TAForm() {
    const { dispatch } = useTimetableContext()

    return (<div>
        <div>TA Form</div>
        <div>
            <input type="text" placeholder="Name" />
            <input type="text" placeholder="Required Shifts" />
            <input type="checkbox" />
            <button className="p-2 bg-blue-300 rounded-xl hover:bg-blue-400">Add TA</button>
        </div>
    </div>)
}

export default function HomeContent() {
    const { state } = useTimetableContext()
    const [formState, setFormState] = useState<FormState>("Hidden")

    const clickAddShift = () => {
        //const shift = new Shift("1", "CS 100", "Monday", "8:30 AM", "9:30 AM", 2, "CS 100 Lab")
        //dispatch(addShift(shift))
        setFormState("Shift")
    }

    const clickAddTA = () => {
        //const ta = new TA("1", "John Doe", 2)
        //dispatch(addTA(ta))
        setFormState("TA")
    }

    return (<div className="flex flex-1 flex-col p-4">
        <div className="">
            <div className="text-xl font-bold">TA Management</div>
            <div className="flex flex-row">
                <div className="flex-1">
                    <div>Shifts:</div>
                    <div>
                        {state.shifts.map(shift => <ShiftDisplay key={shift.id} shift={shift} />)}
                    </div>
                    <div>TAs:</div>
                    <div>
                        {state.tas.map(ta => <TADisplay key={ta.id} ta={ta} />)}
                    </div>
                </div>
                <div className="flex-1">
                    {formState === "Shift" && <ShiftForm />}
                    {formState === "TA" && <TAForm />}
                </div>
            </div>
            <div>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400" onClick={clickAddShift}>Add Shift</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400" onClick={clickAddTA}>Add TAs</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400">Generate Schedule</button>
            </div>

        </div>
        <SchedulerGrid />
    </div>)
}
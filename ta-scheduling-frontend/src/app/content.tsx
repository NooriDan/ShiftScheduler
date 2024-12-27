import SchedulerGrid from "@/components/scheduler-grid";
import { useTimetableContext } from "@/context/app-context";
import { addShift, addTA } from "@/context/app-reducers";
import { Shift, TA } from "@/models/domain";
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

    return (<div>
        <div className="font-bold">Shift Form</div>
        <div>
            <div>
                <label>Series: </label>
                <input type="text" placeholder="Series" className="border rounded p-1" />
            </div>

            <div>
                <label>Required TAs: </label>
                <input type="number" placeholder="Required TAs" className="border rounded p-1" />
            </div>

            <div>
                <label>Day of Week: </label>
                <input type="text" placeholder="Day of Week" className="border rounded p-1" />
            </div>

            <div>
                <label>Start Time: </label>
                <input type="text" placeholder="Start Time" className="border rounded p-1" />
            </div>

            <div>
                <label>End Time: </label>
                <input type="text" placeholder="End Time" className="border rounded p-1" />
            </div>
            <button>Add Shift</button>
        </div>
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
            <button>Add TA</button>
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
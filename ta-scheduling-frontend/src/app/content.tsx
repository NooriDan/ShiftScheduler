import SchedulerGrid, { time_strings } from "@/components/scheduler-grid";
import ShiftForm from "@/components/shift-form";
import TAForm from "@/components/ta-form";
import { useTimetableContext } from "@/context/app-context";
import { removeShift, removeTA } from "@/context/app-reducers";
import { Shift, TA } from "@/models/domain";
import { useState } from "react";

function ShiftDisplay({ shift }: { shift: Shift }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeShift(shift.id))
    }

    return (<div className="flex flex-row">
        <div>{shift.alias} - {shift.day_of_week} {shift.start_time}-{shift.end_time}</div>
        <button className="text-red-500 font-bold hover:cursor-pointer mx-2" onClick={onClick}>X</button>
    </div>)
}

function TADisplay({ ta }: { ta: TA }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeTA(ta.id))
    }

    return (<div className="flex flex-row">
        <div>{ta.name} {ta.is_grad_student ? "Grad" : "Undergrad"} - Required Shifts: {ta.required_shifts}</div>
        <button className="text-red-500 font-bold hover:cursor-pointer mx-2" onClick={onClick}>X</button>
    </div>)
}

type FormState = "Hidden" | "Shift" | "TA";

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
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={clickAddShift}>Add Shift</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={clickAddTA}>Add TAs</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer">Generate Schedule</button>
            </div>

        </div>
        <SchedulerGrid />
    </div>)
}
import SchedulerGrid from "@/components/scheduler-grid";
import ShiftForm from "@/components/shift-form";
import ShiftView from "@/components/shifts-view";
import TAForm from "@/components/ta-form";
import TAView from "@/components/ta-view";
import { useTimetableContext } from "@/context/app-context";
import { removeShift, removeTA, setTimetable } from "@/context/app-reducers";
import { Shift, TA } from "@/models/domain";
import { useState } from "react";

function ShiftDisplay({ shift }: { shift: Shift }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeShift(shift.id))
    }

    return (<div className="flex flex-row">
        <div>{shift.series} - {shift.day_of_week} {shift.start_time}-{shift.end_time}</div>
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
type ViewState = "Schedule" | "Shifts" | "TA"
type GenerationStatus = "Idle" | "Generating" | "Complete"

export default function HomeContent() {
    const { state, dispatch } = useTimetableContext()
    const [formState, setFormState] = useState<FormState>("Hidden")
    const [viewState, setViewState] = useState<ViewState>("Schedule")
    const [generationStatus, setGenerationStatus] = useState<GenerationStatus>("Idle")

    const clickAddShift = () => {
        setFormState("Shift")
    }

    const clickAddTA = () => {
        setFormState("TA")
    }

    const printSchedule = () => {
        console.log(state)
    }

    const generateSchedule = async () => {
        setGenerationStatus("Generating")

        let response = await fetch("http://localhost:8080/schedules", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(state)
        })
        const job_id = await response.text()
        console.log(job_id)

        response = await fetch(`http://localhost:8080/schedules/${job_id}`)
        const schedule = await response.json()
        setGenerationStatus("Complete")
        dispatch(setTimetable(schedule))
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
                <div>Generation Status: {generationStatus}</div>
                {generationStatus === "Complete" && <>
                    <div>Score:</div>
                    <div>Hardscore: {state.score.hardScore}</div>
                    <div>Softscore: {state.score.softScore}</div>
                    <div>Initscore: {state.score.initScore}</div>
                </>}
            </div>

            <div>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={clickAddShift}>Add Shift</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={clickAddTA}>Add TAs</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={generateSchedule}>Generate Schedule</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={printSchedule}>Print Schedule</button>
                <div className="border border-black p-2">
                    <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default" onClick={() => setViewState("Schedule")} disabled={viewState == "Schedule"}>Schedule View</button>
                    <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default" onClick={() => setViewState("Shifts")} disabled={viewState == "Shifts"}>Shifts View</button>
                    <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default" onClick={() => setViewState("TA")} disabled={viewState == "TA"}>TAs View</button>
                </div>
            </div>


        </div>
        {viewState === "Schedule" && <SchedulerGrid />}
        {viewState === "TA" && <TAView />}
        {viewState === "Shifts" && <ShiftView />}
    </div>)
}
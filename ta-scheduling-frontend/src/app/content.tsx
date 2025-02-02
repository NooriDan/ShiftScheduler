"use client"
import SchedulerGrid from "@/components/scheduler-grid";
import ShiftForm from "@/components/shift-form";
import ShiftView from "@/components/shifts-view";
import TAForm from "@/components/ta-form";
import TAView from "@/components/ta-view";
import { useTimetableContext } from "@/context/app-context";
import { addShift, addTA, removeShift, removeTA, setTimetable, updateShift, updateTA } from "@/context/app-reducers";
import { DayOfWeek, Shift, ShiftAssignment, TA, Timetable } from "@/models/domain";
import { convertEuropeanToAmericanTime } from "@/models/time-utils";
import { useState } from "react";

function ShiftDisplay({ shift, onEdit }: { shift: Shift, onEdit: (shift: Shift) => void }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeShift(shift.id))
    }

    return (
        <tr className="border">
            <td className="p-2 border-x">{shift.series}</td>
            <td className="p-2 border-x">{shift.dayOfWeek}</td>
            <td className="p-2 border-x">{convertEuropeanToAmericanTime(shift.startTime)}</td>
            <td className="p-2 border-x">{convertEuropeanToAmericanTime(shift.endTime)}</td>
            <td className="p-2 border-x">{shift.requiredTas}</td>
            <td className="p-2 border-x"><button className="text-red-500 font-bold hover:cursor-pointer mx-2" onClick={onClick}>Delete</button></td>
            <td className="p-2 border-x"><button className="font-bold hover:cursor-pointer mx-2" onClick={() => onEdit(shift)}>Edit</button></td>
        </tr>
    )
}

function TADisplay({ ta, onEdit }: { ta: TA, onEdit: (ta: TA) => void }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeTA(ta.id))
    }

    return (
        <tr className="border">
            <td className="p-2 border-x">{ta.name}</td>
            <td className="p-2 border-x">{ta.id}</td>
            <td className="p-2 border-x">{ta.isGradStudent ? "Grad" : "Undergrad"}</td>
            <td className="p-2 border-x">{ta.requiredShifts}</td>
            <td className="p-2 border-x">{ta.desired.map(s => s.series).join(", ")}</td>
            <td className="p-2 border-x">{ta.undesired.map(s => s.series).join(", ")}</td>
            <td className="p-2 border-x">{ta.unavailable.map(s => s.series).join(", ")}</td>
            <td className="p-2 border-x"><button className="text-red-500 font-bold hover:cursor-pointer mx-2" onClick={onClick}>Delete</button></td>
            <td className="p-2 border-x"><button className="font-bold hover:cursor-pointer mx-2" onClick={() => onEdit(ta)}>Edit</button></td>
        </tr>)

}

type FormState = "Hidden" | "Add Shift" | "Add TA" | "Edit Shift" | "Edit TA";
type ViewState = "Schedule" | "Shifts" | "TA"

// TODO: Create a new formState which is "Edit Shift" and "Edit TA" which will allow the user to edit the shift or TA onclick
// Also store the previous edit state in the state so that the form can be prepopulated with the previous values
// Also make sure that when its changing state to the edit state, once its done it'll get rid of the saved state
// Also update the ShiftForm to be identiical to the TAForm
type GenerationStatus = "Idle" | "Generating" | "Complete"

export default function HomeContent() {
    const { state, dispatch } = useTimetableContext()
    const [formState, setFormState] = useState<FormState>("Hidden")
    const [editState, setEditState] = useState<Shift | TA>()
    const [viewState, setViewState] = useState<ViewState>("Schedule")
    const [generationStatus, setGenerationStatus] = useState<GenerationStatus>("Idle")

    const clickAddShift = () => {
        setFormState("Add Shift")
        setEditState(undefined)
    }

    const clickAddTA = () => {
        setFormState("Add TA")
        setEditState(undefined)
    }

    const clickEditShift = async (shift: Shift) => {
        setEditState(undefined)
        setFormState("Hidden")
        await 1;
        setEditState(shift)
        setFormState("Edit Shift")
    }

    const clickEditTA = async (ta: TA) => {
        setEditState(undefined)
        setFormState("Hidden")
        await 1;
        setEditState(ta)
        setFormState("Edit TA")
    }

    const printSchedule = () => {
        console.log(state)
    }

    const generateSchedule = async () => {
        setGenerationStatus("Generating")

        const shiftAssignments: ShiftAssignment[] = []
        for (const shift of state.shifts) {
            for (let j = 0; j < shift.requiredTas; j++) {
                shiftAssignments.push(new ShiftAssignment(Math.random().toString(36).substring(7), shift))
            }
        }

        state.shiftAssignments = shiftAssignments

        let response = await fetch("http://localhost:8080/schedules", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(state)
        })
        const job_id = (await response.text()).split("\"")[1]

        let status;
        do {
            await new Promise(resolve => setTimeout(resolve, 2000))
            response = await fetch(`http://localhost:8080/schedules/${job_id}`)
            const schedule = await response.json()
            status = schedule.solverStatus
            dispatch(setTimetable(schedule))

        } while (status !== "NOT_SOLVING")

        setGenerationStatus("Complete")
    }

    const fetchDemoData = async () => {
        setEditState(undefined)
        setFormState("Hidden")

        const response = await fetch("http://localhost:8080/demo-data/DemoA")
        const timetable = await response.json()

        const _shifts = timetable.shifts
        const _tas = timetable.tas

        const shifts: Shift[] = _shifts.map((shift: any) => {
            let day_of_week;

            switch (shift.dayOfWeek) {
                case "Mon":
                    day_of_week = DayOfWeek.Monday
                    break
                case "Tue":
                    day_of_week = DayOfWeek.Tuesday
                    break
                case "Wed":
                    day_of_week = DayOfWeek.Wednesday
                    break
                case "Thu":
                    day_of_week = DayOfWeek.Thursday
                    break
                case "Fri":
                    day_of_week = DayOfWeek.Friday
                    break
                case "Sat":
                    day_of_week = DayOfWeek.Saturday
                    break
                case "Sun":
                    day_of_week = DayOfWeek.Sunday
                    break
                default:
                    day_of_week = DayOfWeek.Monday
            }

            const newShift = new Shift(shift.id, shift.series, day_of_week, shift.startTime, shift.endTime, shift.requiredTas)
            newShift.shiftDate = shift.shiftDate
            return newShift
        })

        const tas: TA[] = _tas.map((ta: any) => {
            const newTA = new TA(ta.id, ta.name, ta.requiredShifts)
            newTA.desired = ta.desired.map((shift: any) => shifts.find(s => s.id === shift.id)!)
            newTA.undesired = ta.undesired.map((shift: any) => shifts.find(s => s.id === shift.id)!)
            newTA.unavailable = ta.unavailable.map((shift: any) => shifts.find(s => s.id === shift.id)!)
            newTA.isGradStudent = ta.isGradStudent
            return newTA
        })

        dispatch(setTimetable(new Timetable(timetable.id, shifts, tas, [])))
    }

    const clickHideSide = () => {
        setFormState("Hidden")
        setEditState(undefined)
    }



    return (<div className="flex flex-1 flex-col p-4">
        <div className="">
            <div className="text-3xl font-bold">TA Management</div>
            <div className="flex flex-row">
                <div className="flex-1">
                    <div className="font-bold">Shifts:</div>
                    <table className="table-auto  border-b">
                        <thead>
                            <tr className="border bg-gray-100">
                                <th className="p-2 border-x">Series</th>
                                <th className="p-2 border-x">Day Of the Week</th>
                                <th className="p-2 border-x">Start Time</th>
                                <th className="p-2 border-x">End Time</th>
                                <th className="p-2 border-x">Required TAs</th>
                                <th className="p-2 border-x">Delete button</th>
                                <th className="p-2 border-x">Edit button</th>
                            </tr>
                        </thead>
                        <tbody>
                            {state.shifts.map(shift => <ShiftDisplay key={shift.id} shift={shift} onEdit={clickEditShift} />)}
                        </tbody>
                    </table>
                    <div className="font-bold">TAs:</div>
                    <table className="table-auto border-b">
                        <thead>
                            <tr className="border bg-gray-100">
                                <th className="p-2 border-x">Name</th>
                                <th className="p-2 border-x">Mac ID</th>
                                <th className="p-2 border-x">Type of student</th>
                                <th className="p-2 border-x">Required Shifts</th>
                                <th className="p-2 border-x">Desired Shifts</th>
                                <th className="p-2 border-x">Undesired Shifts</th>
                                <th className="p-2 border-x">Unavailable Shifts</th>
                                <th className="p-2 border-x">Delete button</th>
                                <th className="p-2 border-x">Edit button</th>
                            </tr>
                        </thead>
                        <tbody>
                            {state.tas.map(ta => <TADisplay key={ta.id} ta={ta} onEdit={clickEditTA} />)}
                        </tbody>
                    </table>
                </div>
                <div className="flex-1">
                    <div>
                        <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={clickAddShift}>Add Shift</button>
                        <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={clickAddTA}>Add TAs</button>
                        <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={clickHideSide}>Hide Forms</button>
                        <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={fetchDemoData}>Fetch Demo Data</button>
                        <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={printSchedule}>Print Schedule</button>
                    </div>
                    {formState !== "Hidden" && <>
                        {formState === "Add Shift" && <ShiftForm action={shift => dispatch(addShift(shift))} />}
                        {formState === "Add TA" && <TAForm action={ta => dispatch(addTA(ta))} />}
                        {formState === "Edit Shift" && <ShiftForm shift={editState as Shift} action={shift => dispatch(updateShift(shift))} />}
                        {formState === "Edit TA" && <TAForm ta={editState as TA} action={ta => dispatch(updateTA(ta))} />}
                    </>}
                </div>

            </div>

            <div>
                <div className="font-bold">Generation Status: {generationStatus}</div>
                {generationStatus !== "Idle" && <>
                    <div className="font-bold">Score:</div>
                    <div className="font-bold">Hard score: {state.score.hardScore}</div>
                    <div className="font-bold">Medium score: {state.score.mediumScore}</div>
                    <div className="font-bold">Soft score: {state.score.softScore}</div>
                </>}
            </div>

        </div>
        <div className="font-bold text-2xl pt-2">Scheduling View</div>
        <div>
            <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default font-bold" onClick={() => setViewState("Schedule")} disabled={viewState == "Schedule"}>Schedule View</button>
            <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default font-bold" onClick={() => setViewState("Shifts")} disabled={viewState == "Shifts"}>Shifts View</button>
            <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer disabled:bg-gray-200 disabled:cursor-default  font-bold" onClick={() => setViewState("TA")} disabled={viewState == "TA"}>TAs View</button>
            <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer font-bold " onClick={generateSchedule}>Generate Schedule</button>
        </div>
        {viewState === "Schedule" && <SchedulerGrid />}
        {viewState === "TA" && <TAView />}
        {viewState === "Shifts" && <ShiftView />}
    </div>)
}
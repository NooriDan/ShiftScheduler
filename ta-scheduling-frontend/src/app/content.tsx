import SchedulerGrid from "@/components/scheduler-grid";
import ShiftForm from "@/components/shift-form";
import ShiftView from "@/components/shifts-view";
import TAForm from "@/components/ta-form";
import TAView from "@/components/ta-view";
import { useTimetableContext } from "@/context/app-context";
import { removeShift, removeTA, setTimetable } from "@/context/app-reducers";
import { DayOfWeek, Shift, ShiftAssignment, TA, Timetable } from "@/models/domain";
import { convertEuropeanToAmericanTime } from "@/models/time-utils";
import { useState } from "react";

function ShiftDisplay({ shift }: { shift: Shift }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeShift(shift.id))
    }

    return (<div className="flex flex-row">
        <div>{shift.series} - {shift.dayOfWeek} {convertEuropeanToAmericanTime(shift.startTime)}-{convertEuropeanToAmericanTime(shift.endTime)}</div>
        <button className="text-red-500 font-bold hover:cursor-pointer mx-2" onClick={onClick}>X</button>
    </div>)
}

function TADisplay({ ta }: { ta: TA }) {
    const { dispatch } = useTimetableContext()

    const onClick = () => {
        dispatch(removeTA(ta.id))
    }

    return (<div className="flex flex-row">
        <div>{ta.name} {ta.isGradStudent ? "Grad" : "Undergrad"} - Required Shifts: {ta.requiredShifts}</div>
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
        const job_id = (await response.text()).split("\"")[1]

        do {
            response = await fetch(`http://localhost:8080/schedules/${job_id}`)
            const schedule = await response.json()

            if (schedule.score.hardScore !== 0 || schedule.score.softScore !== 0) {
                setGenerationStatus("Complete")
                console.log(schedule)
                dispatch(setTimetable(schedule))
                break
            }

            await new Promise(resolve => setTimeout(resolve, 1000))
        }
        while (true)
    }

    const fetchDemoData = async () => {
        const response = await fetch("http://localhost:8080/demo-data/DemoA")
        const timetable = await response.json()

        const _shifts = timetable.shifts
        const _tas = timetable.tas
        const _shift_assignments = timetable.shiftAssignments

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

        const shift_assignments: ShiftAssignment[] = _shift_assignments.map((assignment: any) => {
            const ta = tas.find(ta => ta.id === assignment.ta_id)
            const shift = shifts.find(shift => shift.id === assignment.shift.id)!
            return new ShiftAssignment(assignment.id, shift, ta)
        })

        dispatch(setTimetable(new Timetable(timetable.id, shifts, tas, shift_assignments)))
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
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={fetchDemoData}>Fetch Demo Data</button>
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
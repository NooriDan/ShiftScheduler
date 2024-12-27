import SchedulerGrid from "@/components/scheduler-grid";
import { useTimetableContext } from "@/context/app-context";
import { addShift, addTA } from "@/context/app-reducers";
import { Shift, TA } from "@/models/domain";

function ShiftDisplay({ shift }: { shift: Shift }) {
    return <div>{shift.alias} - {shift.day_of_week} {shift.start_time}-{shift.end_time}</div>
}

function TADisplay({ ta }: { ta: TA }) {
    return <div>{ta.name} {ta.is_grad_student ? "Grad" : "Undergrad"} - Required Shifts: {ta.required_shifts} </div>
}

export default function HomeContent() {
    const { state, dispatch } = useTimetableContext()

    const clickAddShift = () => {
        const shift = new Shift("1", "CS 100", "Monday", "8:30 AM", "9:30 AM", 2, "CS 100 Lab")
        dispatch(addShift(shift))
    }

    const clickAddTA = () => {
        const ta = new TA("1", "John Doe", 2)
        dispatch(addTA(ta))
    }

    return (<div className="flex flex-1 flex-col p-4">
        <div className="">
            <div className="text-xl font-bold">TA Management</div>
            <div>

                <div>Shifts:</div>
                <div>
                    {state.shifts.map(shift => <ShiftDisplay key={shift.id} shift={shift} />)}
                </div>
                <div>TAs:</div>
                <div>
                    {state.tas.map(ta => <TADisplay key={ta.id} ta={ta} />)}
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
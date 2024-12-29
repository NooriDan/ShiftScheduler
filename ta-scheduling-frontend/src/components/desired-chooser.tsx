import { Shift } from "@/models/domain";
import { ActionDispatch, useEffect, useReducer, useState } from "react";

export function reducer(state: Shift[], action: any) {
    switch (action.type) {
        case "add":
            return [...state, action.payload]
        case "remove":
            return state.filter(item => item !== action.payload)
        default:
            return state
    }
}

export interface DesiredChooserProps {
    shifts: Shift[]
    dispatch: ActionDispatch<any>
    available: Shift[]
}

export function addShift(shift: Shift) {
    return { type: "add", payload: shift }
}

export function removeShift(shift: Shift) {
    return { type: "remove", payload: shift }
}

export default function DesiredChooser({ shifts, dispatch, available }: DesiredChooserProps) {
    const [current, setCurrent] = useState<string>("Choose option")

    const addClick = () => {
        console.log("Adding shift", current)
        if (current && current !== "Choose option") {

            dispatch(addShift(available.find(shift => shift.id === current) as Shift))
        }
    }

    useEffect(() => {
        setCurrent(available.length > 0 ? available[0].id : "Choose option")
    }, [available])

    return (<div className="border border-black p-2">
        <div className="border border-black p-2">
            <label>Add desired shifts: </label>
            <select className="rounded border border-black p-2" value={current} onChange={e => setCurrent(e.target.value)}>
                <option disabled value="Choose option">Choose option</option>
                {available.map((shift) => <option key={shift.id} value={shift.id}>{shift.series}</option>)}
            </select>
            <button type="button" className="p-2 mx-2 bg-blue-300 rounded-xl hover:bg-blue-400 hover:cursor-pointer" onClick={addClick}>Add</button>
        </div>
        <div className="border border-black p-2">
            {shifts.filter(shift => shift).map(shift => <div key={shift.id}>{shift.series} <button onClick={() => dispatch(removeShift(shift))}>Remove</button></div>)}
        </div>
    </div>)
}
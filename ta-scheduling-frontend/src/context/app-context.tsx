import { DayOfWeek, Shift, Timetable } from "@/models/domain";
import { createContext, Dispatch, useContext, useReducer } from "react";
import { reducer, TimetableActions } from "./app-reducers";

// Initial timetable state
const initialState = new Timetable("", [ new Shift("1", "L01", DayOfWeek.Monday, "8:30 AM", "10:30 AM", 2)], [], [], 0)

// Context properties
export interface ITimetableContextProps {
    state: Timetable,
    dispatch: Dispatch<TimetableActions>
}

// Context
export const TimetableContext = createContext<ITimetableContextProps>({ state: initialState, dispatch: () => { } })

// Hook
export function useTimetableContext() {
    return useContext(TimetableContext)
}

// Provider
export function TimetableProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState)

    return (
        <TimetableContext.Provider value={{ state, dispatch }}>
            {children}
        </TimetableContext.Provider>
    )
}


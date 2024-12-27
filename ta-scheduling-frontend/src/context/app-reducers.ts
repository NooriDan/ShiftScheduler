import { Shift, TA, Timetable } from "@/models/domain";

// Action map
type ActionMap<M extends { [index: string]: any }> = {
    [Key in keyof M]: M[Key] extends undefined
    ? {
        type: Key;
    }
    : {
        type: Key;
        payload: M[Key];
    }
};


// Actions
export enum TimetableActionTypes {
    ADD_SHIFT = 'timetable.addShift',
    ADD_TA = 'timetable.addTA',
    REMOVE_SHIFT = 'timetable.removeShift',
    REMOVE_TA = 'timetable.removeTA',
    SET_TIMETABLE = 'timetable.setTimetable'
}

// Action
export type TimetablePayload = {
    [TimetableActionTypes.ADD_SHIFT]: Shift
    [TimetableActionTypes.ADD_TA]: TA
    [TimetableActionTypes.REMOVE_SHIFT]: string
    [TimetableActionTypes.REMOVE_TA]: string
    [TimetableActionTypes.SET_TIMETABLE]: Timetable
}

// Action map of timetable actions
export type TimetableActions = ActionMap<TimetablePayload>[keyof ActionMap<TimetablePayload>];

// Reducer
export function reducer(state: Timetable, action: TimetableActions): Timetable {
    switch (action.type) {
        case TimetableActionTypes.ADD_SHIFT:

            const shift = action.payload
            // Add unique id
            shift.id = Math.random().toString(36).substring(7)
            return { ...state, shifts: [...state.shifts, shift] }
        case TimetableActionTypes.ADD_TA:

            const ta = action.payload
            // Add unique id
            ta.id = Math.random().toString(36).substring(7)
            return { ...state, tas: [...state.tas, ta] }
        case TimetableActionTypes.REMOVE_SHIFT:

            const shiftId = action.payload
            return { ...state, shifts: state.shifts.filter(shift => shift.id !== shiftId) }
        case TimetableActionTypes.REMOVE_TA:

            const taId = action.payload
            return { ...state, tas: state.tas.filter(ta => ta.id !== taId) }
        default:
            return state
    }
}

// Action Creators
export function addShift(shift: Shift): TimetableActions {
    return { type: TimetableActionTypes.ADD_SHIFT, payload: shift }
}

export function addTA(ta: TA): TimetableActions {
    return { type: TimetableActionTypes.ADD_TA, payload: ta }
}

export function removeShift(shiftId: string): TimetableActions {
    return { type: TimetableActionTypes.REMOVE_SHIFT, payload: shiftId }
}

export function removeTA(taId: string): TimetableActions {
    return { type: TimetableActionTypes.REMOVE_TA, payload: taId }
}

export function setTimetable(timetable: Timetable): TimetableActions {
    return { type: TimetableActionTypes.SET_TIMETABLE, payload: timetable }
}
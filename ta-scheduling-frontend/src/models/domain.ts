export enum DayOfWeek {
    Monday = "Monday",
    Tuesday = "Tuesday",
    Wednesday = "Wednesday",
    Thursday = "Thursday",
    Friday = "Friday",
    Saturday = "Saturday",
    Sunday = "Sunday"
}

export class Shift {
    id: string
    series: string
    dayOfWeek: DayOfWeek
    startTime: string
    endTime: string
    requiredTas: number
    // Optional
    alias: string = "DEFAULT"
    shiftDate: string = "1900-01-01"

    constructor(id: string, series: string, day_of_week: DayOfWeek, start_time: string, end_time: string, required_tas: number, alias: string = "DEFAULT", shift_date: string = "1900-01-01") {
        this.id = id
        this.series = series
        this.dayOfWeek = day_of_week
        this.startTime = start_time
        this.endTime = end_time
        this.requiredTas = required_tas
        this.alias = alias
        this.shiftDate = shift_date
    }
}

export class TA {
    id: string
    name: string
    requiredShifts: number
    desired: Shift[] = []
    undesired: Shift[] = []
    unavailable: Shift[] = []
    // favourite_partners: TA[] = None
    isGradStudent: boolean = true

    constructor(id: string, name: string, required_shifts: number, desired: Shift[] = [], undesired: Shift[] = [], unavailable: Shift[] = [], is_grad_student: boolean = true) {
        this.id = id
        this.name = name
        this.requiredShifts = required_shifts
        this.desired = desired
        this.undesired = undesired
        this.unavailable = unavailable
        this.isGradStudent = is_grad_student
    }


}

export function get_status_for_shift(ta: TA, shift: Shift): string {
    if (ta.desired.map(shift => shift.id).includes(shift.id))
        return 'Desired'
    if (ta.undesired.map(shift => shift.id).includes(shift.id))
        return 'Undesired'
    if (ta.unavailable.map(shift => shift.id).includes(shift.id))
        return 'Unavailable'
    return 'Neutral'
}

export class ShiftAssignment {
    id: string
    assignedTa?: TA
    shift: Shift

    constructor(id: string, shift: Shift, assigned_ta?: TA) {
        this.id = id
        this.assignedTa = assigned_ta
        this.shift = shift
    }
}

export class Score {
    hardScore: number
    softScore: number
    mediumScore: number

    constructor(hardScore: number = 0, softScore: number = 0, mediumScore: number = 0) {
        this.hardScore = hardScore
        this.softScore = softScore
        this.mediumScore = mediumScore
    }
}

export class Timetable {
    id: string
    // problem facts
    shifts: Shift[]
    tas: TA[]
    // planning entities
    shiftAssignments: ShiftAssignment[]
    score: Score

    constructor(id: string, shifts: Shift[], tas: TA[], shift_assignments: ShiftAssignment[], score: Score = new Score()) {
        this.id = id
        this.shifts = shifts
        this.tas = tas
        this.shiftAssignments = shift_assignments
        this.score = score
    }
}
